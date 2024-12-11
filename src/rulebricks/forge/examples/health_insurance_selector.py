# For development, use
# PYTHONPATH=$PYTHONPATH:$(pwd)/src python3 src/rulebricks/forge/examples/health_insurance_selector.py

from rulebricks.forge import Rule

import rulebricks as rb

def create_health_insurance_selector():
    # Initialize the rule
    rule = Rule()

    # Set basic metadata
    rule.set_name("Health Insurance Account Selector") \
        .set_description("Assists individuals in selecting the most suitable health insurance account option based on their healthcare needs, financial situation, and preferences.")

    # Define request fields with a more intuitive interface
    age = rule.add_number_field("age", "Age of the individual", 0)
    income = rule.add_number_field("income", "Annual income of the individual", 0)
    chronic = rule.add_boolean_field("chronic_conditions", "Whether the individual has chronic conditions", False)
    deductible = rule.add_number_field("deductible_preference", "Preferred deductible amount", 0)
    frequency = rule.add_string_field("medical_service_frequency", "Frequency of medical service needs", "")

    # Define response fields
    rule.add_string_response("recommended_plan", "Recommended health insurance plan", "")
    rule.add_number_response("estimated_premium", "Estimated monthly premium", 0)

    # Define conditions and outcomes
    # Note the named parameters need to match the *field* names defined above
    # (not the variable names)
    rule.when(
        age=age.between(18,35),
        income=income.between(50000, 75000),
        chronic_conditions=chronic.equals(True),
        deductible_preference=deductible.between(500, 1000),
        medical_service_frequency=frequency.equals("monthly")
    ).then(
        recommended_plan="HSA",
        estimated_premium=2000
    )

    # The order in which conditions are defined matters significantly
    # The first one that matches will be executed
    # This is the second condition row in the table
    rule.when(
        age=age.greater_than(35),
        income=income.greater_than(75000),
        chronic_conditions=chronic.equals(False),
        deductible_preference=deductible.greater_than(1000),
        medical_service_frequency=frequency.equals("quarterly")
    ).then(
        recommended_plan="PPO",
        estimated_premium=3000
    )

    # Use .any() method to create an OR across conditions for a specific outcome
    rule.any(
        age=age.greater_than(60),
        income=income.greater_than(200000),
        chronic_conditions=chronic.equals(False),
    ).then(
        recommended_plan="PPO",
        estimated_premium=2500
    )

    # A fallback condition that will be executed if no other conditions match
    # Helps to ensure that the rule always produces a result
    # And prevents API errors when an outcome is not able to be determined
    rule.when(
        # Nothing here!
    ).then(
        recommended_plan="Unknown"
    )

    return rule

if __name__ == "__main__":
    # Create and preview the rule's conditions...
    rule = create_health_insurance_selector()
    print(rule.to_table())

    # Export the rule to a .rbx file that can be imported into Rulebricks manually
    # rule.export()

    # Or, import the rule directly into your Rulebricks workspace
    rb.configure(
        api_key="XXXXXXX-XXXX-XXXX-XXXX-XXXXXXXXXXXX" # Replace with your API key
    )

    # Import the rule, but don't immediately publish it...
    created_rule = rb.assets.import_rule(rule=rule, publish=False)

    # The new rule should appear in your Rulebricks workspace if we list all rules
    print(rb.assets.list_rules())

    # The URL to edit the rule in the Rulebricks web app should work!
    print(rule.get_editor_url())

    # We can retrieve the rule data we just created using its returned ID
    rule_json = rb.assets.export_rule(id=created_rule.id)

    # Create a Rule object to represent it
    # This is useful if you want to modify the rule using the SDK
    located_rule = Rule.from_json(rule_json)

    # Update the rule– but let's publish it this time
    updated_rule = rb.assets.import_rule(rule=located_rule, publish=True)

    # Let's try solving the rule with some test data!
    test_data = {
        "age": 25,
        "income": 60000,
        "chronic_conditions": True,
        "deductible_preference": 750,
        "medical_service_frequency": "monthly"
    }
    print(updated_rule)
    test_data_solution = rb.rules.solve(
        slug=updated_rule.slug,
        request=test_data
    )
    print(test_data_solution)

    # Delete the rule
    # rb.assets.delete_rule(id=updated_rule.id)
