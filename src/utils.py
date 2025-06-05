from typing import List
from termcolor import colored


def estimate_remaining_time(
    iteration_times: List[float],
    total_iterations: int,
    current_iteration: int,
    string_process: str,
) -> None:
    # Calculate the average time per iteration so far
    avg_time_per_iteration = sum(iteration_times) / len(iteration_times)

    # Estimate the remaining time
    remaining_iterations = total_iterations - current_iteration
    estimated_remaining_time = avg_time_per_iteration * remaining_iterations

    hours, remainder = divmod(estimated_remaining_time, 3600)
    minutes, seconds = divmod(remainder, 60)
    time_string = f"Estimated remaining time for {string_process}: {int(hours)}:{int(minutes):02d}:{int(seconds):02d}"
    colored_string = colored(time_string, "green")

    print(colored_string)
