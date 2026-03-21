from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

from core.database import Base
from database.models import MessageRole
from services.rubric_mapper import RubricMapper
from services.session_manager import SessionManager
from services.symptom_extractor import SymptomExtractor


async def _build_session_manager():
    engine = create_async_engine("sqlite+aiosqlite:///:memory:")
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    session_factory = async_sessionmaker(engine, expire_on_commit=False)
    db = session_factory()
    return engine, db, SessionManager(db)


async def test_rule_based_extractor_produces_structured_rubrics():
    extractor = SymptomExtractor()

    extracted = await extractor.extract(
        "I have a throbbing headache that gets worse from light and noise. "
        "I feel fear at night and I get restless."
    )

    rubric_paths = {symptom.rubric_path for symptom in extracted if symptom.rubric_path}
    dimensions = {symptom.dimension for symptom in extracted}

    assert "Head > Pain > Throbbing" in rubric_paths
    assert "Head > Pain > Light aggravates" in rubric_paths
    assert "Head > Pain > Worse from noise" in rubric_paths
    assert "Mind > Fear > Night" in rubric_paths
    assert "location" in dimensions
    assert "general" in dimensions


def test_rubric_mapper_requires_head_context_for_headache_rubrics():
    mapper = RubricMapper()

    assert mapper.map_symptom("my heart is pounding", dimension="sensation") == (None, None, 0.0)
    assert mapper.map_symptom("light bothers my eyes", dimension="modality_aggravation") == (None, None, 0.0)
    assert mapper.map_symptom(
        "light bothers my eyes",
        dimension="modality_aggravation",
        rubric_hint="Head > Pain > Light aggravates",
    ) == (None, None, 0.0)


async def test_rule_based_extractor_uses_patient_text_for_context_guard():
    extractor = SymptomExtractor()

    extracted = await extractor.extract("My heart is pounding and light bothers my eyes.")

    assert extracted == []


async def test_session_manager_counts_unique_rubrics_for_analysis_ready():
    engine, db, manager = await _build_session_manager()
    try:
        session = await manager.create_session()
        message = await manager.store_message(session.id, MessageRole.user, "case intake")
        extractor = SymptomExtractor()

        extracted = await extractor.extract(
            "I have a throbbing headache that gets worse from light and noise. "
            "I feel fear at night and I get restless."
        )

        await manager.update_symptoms(session.id, extracted, message.id)
        await manager.update_symptoms(session.id, extracted, message.id)

        rubric_paths = await manager.get_session_rubric_paths(session.id)
        state = await manager.get_session_state(session.id)

        assert await manager.is_analysis_ready(session.id) is True
        assert len(rubric_paths) == 5
        assert state is not None
        assert "restlessness" in state.generals
    finally:
        await db.close()
        await engine.dispose()


async def test_non_rubric_general_symptoms_do_not_block_follow_up_question():
    engine, db, manager = await _build_session_manager()
    try:
        session = await manager.create_session()
        message = await manager.store_message(session.id, MessageRole.user, "case intake")
        extractor = SymptomExtractor()

        extracted = await extractor.extract(
            "I have a throbbing headache that gets worse from light. "
            "I feel fear at night and my sleep is disturbed."
        )

        await manager.update_symptoms(session.id, extracted, message.id)

        assert await manager.is_analysis_ready(session.id) is False
        assert "generals" in await manager.get_missing_dimensions(session.id)
        assert await manager.plan_next_question(session.id) == "How is your energy, sleep, and appetite generally?"
    finally:
        await db.close()
        await engine.dispose()


async def test_refinement_question_is_used_when_dimensions_are_filled_but_evidence_is_thin():
    engine, db, manager = await _build_session_manager()
    try:
        session = await manager.create_session()
        message = await manager.store_message(session.id, MessageRole.user, "case intake")
        extractor = SymptomExtractor()

        extracted = await extractor.extract(
            "I have a throbbing headache that gets worse from light. "
            "I feel anxious and restless."
        )

        await manager.update_symptoms(session.id, extracted, message.id)

        assert await manager.is_analysis_ready(session.id) is False
        assert await manager.get_missing_dimensions(session.id) == []
        assert await manager.plan_next_question(session.id) == (
            "Along with the complaint, are there any marked emotional changes such as fear, anxiety, irritability, or restlessness?"
        )
    finally:
        await db.close()
        await engine.dispose()


async def test_rubric_backed_evidence_counts_use_extracted_dimension():
    engine, db, manager = await _build_session_manager()
    try:
        session = await manager.create_session()
        message = await manager.store_message(session.id, MessageRole.user, "case intake")
        extractor = SymptomExtractor()

        extracted = await extractor.extract(
            "I have a throbbing headache that gets worse from light. "
            "I feel fear at night and I get restless."
        )

        await manager.update_symptoms(session.id, extracted, message.id)

        counts = await manager._get_rubric_backed_dimension_counts(session.id)
        assert counts.get("sensation") == 1
        assert counts.get("location", 0) == 0
    finally:
        await db.close()
        await engine.dispose()
