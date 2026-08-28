import json
from advanced import diagnose_advanced


def load_incidents():
    with open("data/incidents.json", "r", encoding="utf-8") as file:
        return json.load(file)


def evaluate(diagnose_fn):
    incidents = load_incidents()

    correct = 0
    results = []

    for incident in incidents:
        predicted = diagnose_fn(incident)
        expected = incident["expected_cause"]
        is_correct = predicted == expected

        if is_correct:
            correct += 1

        results.append(
            {
                "id": incident["id"],
                "service": incident["service"],
                "expected": expected,
                "predicted": predicted,
                "correct": is_correct
            }
        )

    accuracy = correct / len(incidents)

    return {
        "correct": correct,
        "total": len(incidents),
        "accuracy": accuracy,
        "results": results
    }


if __name__ == "__main__":
    report = evaluate(diagnose_advanced)

    print("\nAdvanced Evaluation")
    print("-------------------")
    print(
        f"Accuracy: {report['correct']}/{report['total']} "
        f"({report['accuracy'] * 100:.1f}%)"
    )

    print("\nCases:")
    for result in report["results"]:
        symbol = "PASS" if result["correct"] else "FAIL"

        print(
            f"{symbol} | Case {result['id']} | "
            f"expected={result['expected']} | "
            f"predicted={result['predicted']}"
        )
