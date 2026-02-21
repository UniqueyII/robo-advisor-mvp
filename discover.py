import src.data_fetcher
import inspect

print("=== FUNCTIONS in data_fetcher.py ===")
for name, func in inspect.getmembers(src.data_fetcher, inspect.isfunction):
    print(f"- {name}")

print("\n=== CLASSES in data_fetcher.py ===")
for name, cls in inspect.getmembers(src.data_fetcher, inspect.isclass):
    print(f"- {name}")

print("\n=== CONSTANTS/VARIABLES ===")
for name in dir(src.data_fetcher):
    if not name.startswith('_') and not inspect.isfunction(getattr(src.data_fetcher, name)) and not inspect.isclass(getattr(src.data_fetcher, name)):
        print(f"- {name}")
