def run_benchmark(config_version):
    test_cases = load_test_cases()
    results = []
    
    for case in test_cases:
        response = simulate_agent(case.input, config_version)
        score = evaluate_response(
            response,
            case.expected_output,
            case.metrics)
        results.append(score)
    
    save_results(config_version, results)
    return results.mean()