import argparse

from server.agents.dsl_runner import DSLScenarioRunner


def main() -> None:
    parser = argparse.ArgumentParser(description="DSL scenario text runner")
    parser.add_argument(
        "--scenario",
        default="server/scenarios/scenario.json",
        help="Path to scenario.json",
    )
    parser.add_argument(
        "--emergency-keywords",
        default="server/scenarios/emergency_keywords.json",
        help="Path to emergency keywords JSON",
    )
    parser.add_argument(
        "--emergency-flow",
        default="server/scenarios/EMERGENCY_FLOW.json",
        help="Path to emergency flow JSON",
    )
    parser.add_argument(
        "--show-slots",
        action="store_true",
        help="Print slot state after each turn.",
    )
    args = parser.parse_args()

    runner = DSLScenarioRunner(
        scenario_path=args.scenario,
        emergency_keywords_path=args.emergency_keywords,
        emergency_flow_path=args.emergency_flow,
    )

    response = runner.process("")
    if response.text:
        print(response.text)

    while not response.is_complete:
        user_input = input("> ").strip()
        response = runner.process(user_input)
        if response.text:
            print(response.text)
        if args.show_slots:
            print(response.slots)

    if args.show_slots:
        print("Final slots:", response.slots)


if __name__ == "__main__":
    main()
