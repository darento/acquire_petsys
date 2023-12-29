from typing import List
from tqdm   import tqdm
import time

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
    
def progress_bar(total_time: float) -> tqdm:
    # Create a progress bar
    with tqdm(total=total_time, desc="Progress", bar_format="{l_bar}{bar}") as pbar:
        for i in range(int(total_time)):
            time.sleep(1)  # Sleep for 1 second
            pbar.update(1)  # Update the progress bar