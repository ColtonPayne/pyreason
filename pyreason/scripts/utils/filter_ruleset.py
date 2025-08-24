def filter_ruleset(queries, rules):
    """
    Filter the ruleset based on the queries provided.

    :param queries: List of Query objects
    :param rules: List of Rule objects
    :return: List of Rule objects that are applicable to the queries
    """

    # Helper function to collect all rules that can support making a given rule true
    def applicable_rules_from_query(query, visited):
        # Avoid revisiting the same predicate to prevent infinite recursion
        if query in visited:
            return []
        visited.add(query)

        applicable = []
        for rule in rules:
            if query == rule.get_target():
                applicable.append(rule)
                for clause in rule.get_clauses():
                    applicable.extend(applicable_rules_from_query(clause[1], visited))

        return applicable

    # Collect applicable rules for each query and eliminate duplicates
    filtered_rules = []
    for q in queries:
        filtered_rules.extend(applicable_rules_from_query(q.get_predicate(), set()))

    # Use set to avoid duplicates if a rule supports multiple queries
    return list(set(filtered_rules))
