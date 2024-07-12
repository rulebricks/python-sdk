from rulebricks import RuleBuilder, RuleType
from rulebricks.forge import BooleanOperator, NumberOperator, StringOperator, boolean_op, number_op, string_op

def main():
    demo_rule = RuleBuilder()

    # Set name and description
    demo_rule.set_name("Health Insurance Account Selector")
    demo_rule.set_description("Assists individuals in selecting the most suitable health insurance account option based on their healthcare needs, financial situation, deductible preferences, frequency of medical service needs, etc.")

    # Define request schema
    demo_rule.add_request_field("age", "Age", RuleType.NUMBER, "Age of the individual", 0)
    demo_rule.add_request_field("income", "Income", RuleType.NUMBER, "Annual income of the individual", 0)
    demo_rule.add_request_field("chronic_conditions", "Chronic Conditions", RuleType.BOOLEAN, "Whether the individual has chronic conditions", False)
    demo_rule.add_request_field("deductible_preference", "Deductible Preference", RuleType.NUMBER, "Preferred deductible amount", 0)
    demo_rule.add_request_field("medical_service_frequency", "Medical Service Frequency", RuleType.STRING, "Frequency of medical service needs", "")
    demo_rule.add_request_field("preferences.deductible", "Deductible Preference", RuleType.NUMBER, "Preferred deductible amount", 0)
    demo_rule.add_request_field("health.medical_service_frequency", "Medical Service Frequency", RuleType.STRING, "Frequency of medical service needs", "")

    # Define response schema
    demo_rule.add_response_field("recommended_plan", "Recommended Plan", RuleType.STRING, "Recommended health insurance plan", "")
    demo_rule.add_response_field("estimated_premium", "Estimated Premium", RuleType.NUMBER, "Estimated monthly premium", 0)

    # Create conditions
    condition1 = demo_rule.add_condition()
    demo_rule.update_condition(condition1, "age", *number_op(NumberOperator.BETWEEN)(26, 35))
    demo_rule.update_condition(condition1, "income", *number_op(NumberOperator.BETWEEN)(50000, 75000))
    demo_rule.update_condition(condition1, "chronic_conditions", *boolean_op(BooleanOperator.IS_TRUE)())
    demo_rule.update_condition(condition1, "deductible_preference", *number_op(NumberOperator.BETWEEN)(500, 1000))
    demo_rule.update_condition(condition1, "medical_service_frequency", *string_op(StringOperator.EQUALS)("monthly"))
    demo_rule.set_condition_response(condition1, "recommended_plan", "HSA")
    demo_rule.set_condition_response(condition1, "estimated_premium", 2000)

    condition2 = demo_rule.add_condition()
    demo_rule.update_condition(condition2, "age", *number_op(NumberOperator.GREATER_THAN)(35))
    demo_rule.update_condition(condition2, "income", *number_op(NumberOperator.GREATER_THAN)(75000))
    demo_rule.update_condition(condition2, "chronic_conditions", *boolean_op(BooleanOperator.IS_FALSE)())
    demo_rule.update_condition(condition2, "deductible_preference", *number_op(NumberOperator.GREATER_THAN)(1000))
    demo_rule.update_condition(condition2, "medical_service_frequency", *string_op(StringOperator.EQUALS)("quarterly"))
    demo_rule.set_condition_response(condition2, "recommended_plan", "PPO")
    demo_rule.set_condition_response(condition2, "estimated_premium", 3000)

    # Create an empty condition
    condition3 = demo_rule.add_condition()

    # Print, pretty-print, and export rule
    print(demo_rule.to_table())
    print(demo_rule.to_json())
    demo_rule.export()

if __name__ == "__main__":
    main()
