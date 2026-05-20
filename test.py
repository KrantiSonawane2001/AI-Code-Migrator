from validators import validate_code_input
from graph import run_migration_pipeline

# Test 1 — Empty input
print("Test 1 — Empty:")
v = validate_code_input("")
print(f"Valid: {v['valid']} | Reason: {v['reason']}")

# Test 2 — Plain English
print("\nTest 2 — Plain English:")
v = validate_code_input("Please help me migrate my Java code to modern version")
print(f"Valid: {v['valid']} | Reason: {v['reason']}")

# Test 3 — Too short
print("\nTest 3 — Too short:")
v = validate_code_input("int x = 5;")
print(f"Valid: {v['valid']} | Reason: {v['reason']}")

# Test 4 — Valid code
print("\nTest 4 — Valid Java:")
v = validate_code_input("""
public class Hello {
    public static void main(String[] args) {
        System.out.println("Hello");
    }
}
""")
print(f"Valid: {v['valid']} | Reason: {v['reason']}")
print(f"Warnings: {v['warnings']}")