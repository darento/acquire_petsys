from typing import List

def estimate_remaining_time(iteration_times: List[float], 
                            total_iterations: int, 
                            current_iteration: int,
                            string_process: str) -> None:
    # Calculate the average time per iteration so far
    avg_time_per_iteration = sum(iteration_times) / len(iteration_times)

    # Estimate the remaining time
    remaining_iterations = total_iterations - current_iteration
    estimated_remaining_time = avg_time_per_iteration * remaining_iterations

    print(f"Estimated remaining time for {string_process}: {round(estimated_remaining_time, 1)} seconds")
    
