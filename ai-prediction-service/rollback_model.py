import argparse
import registry

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("model_name")
    args = parser.parse_args()

    registry.rollback(args.model_name)
    active = registry.get_active_model(args.model_name)
    print(f"Rolled back. Now ACTIVE: {args.model_name} -> version {active['version']}")