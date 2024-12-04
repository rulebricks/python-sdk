from rulebricks.forge import Rule

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

    # Define conditions with a more intuitive interface
    rule.when(
        age=age.between(18,35),
        income=income.between(50000, 75000),
        chronic=chronic.equals(True),
        deductible=deductible.between(500, 1000),
        frequency=frequency.equals("monthly")
    ).then(
        recommended_plan="HSA",
        estimated_premium=2000
    )

    rule.when(
        age=age.greater_than(35),
        income=income.greater_than(75000),
        chronic=chronic.equals(False),
        deductible=deductible.greater_than(1000),
        frequency=frequency.equals("quarterly")
    ).then(
        recommended_plan="PPO",
        estimated_premium=3000
    )

    return rule

if __name__ == "__main__":
    # Create and export the rule
    rule = create_health_insurance_selector()
    print(rule.to_json())
