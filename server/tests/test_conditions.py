from server.agents.dsl_runner import DSLScenarioRunner


def test_eval_condition_equals_and_bool(tmp_path) -> None:
    scenario_path = "server/scenarios/scenario.json"
    runner = DSLScenarioRunner(scenario_path)
    runner.slot_manager.set("consent_ok", True)

    assert runner._eval_condition("consent_ok == true") is True
    assert runner._eval_condition("consent_ok == false") is False


def test_eval_condition_string_and_contains_any() -> None:
    scenario_path = "server/scenarios/scenario.json"
    runner = DSLScenarioRunner(scenario_path)
    runner.slot_manager.set("symptom_track", "HEADACHE")
    runner.slot_manager.set("allergy_history", "숨이 차고 두드러기가 났어요")

    assert runner._eval_condition("symptom_track == 'HEADACHE'") is True
    assert (
        runner._eval_condition("allergy_history containsAny(['숨', '호흡곤란'])")
        is True
    )
