import csv
import numpy as np

def read_power_table(filename):
    """Reads the power table from a CSV file, supporting multiple modes per subsystem."""
    subsystems = {}
    mode_list = []  # Flattened list of all modes for indexing
    mode_indices = {}  # Map subsystem names to mode indices
    with open(filename, mode='r') as file:
        reader = csv.DictReader(file)
        for row in reader:
            name = row["Subsystem"]
            mode = {
                "subsystem": name,
                "mode": row["Mode"],
                "voltage": float(row["Voltage (V)"] ),
                "duty_cycle": float(row["Duty Cycle"].strip('%')) / 100.0,  # Convert percentage to fraction
                "equiv_minutes": int(float(row["Equiv. Minutes"])),
                "power": float(row["Power (W)"] ),
                "energy": float(row["Energy (Wh)"] ),
                "current": float(row["Dis. Current (A)"])
            }
            if name not in subsystems:
                subsystems[name] = []
                mode_indices[name] = []
            subsystems[name].append(mode)
            mode_list.append(mode)  # Store in flat list
            mode_indices[name].append(len(mode_list) - 1)  # Track mode indices for each subsystem
    return subsystems, mode_list, mode_indices

def generate_schedule(subsystems, mode_list, mode_indices, orbit_duration=90, time_step=2):
    """Generates a schedule that ensures correct duty cycles and balances power consumption."""
    time_slots = orbit_duration // time_step
    schedule = np.zeros((len(mode_list), time_slots), dtype=int)
    
    for sub, modes in subsystems.items():
        total_slots = sum(int(mode["duty_cycle"] * time_slots) for mode in modes)
        if total_slots > time_slots:
            raise ValueError(f"Total duty cycle for {sub} exceeds 100% of available slots.")
        
        slot_indices = list(range(time_slots))
        np.random.shuffle(slot_indices)  # Randomize slot selection to distribute power load
        
        mode_start = 0
        for mode, mode_idx in zip(modes, mode_indices[sub]):
            active_slots = int(mode["duty_cycle"] * time_slots)
            selected_slots = sorted(slot_indices[mode_start:mode_start + active_slots])
            mode_start += active_slots
            
            for t in selected_slots:
                # Ensure no other mode of the same subsystem is active at this time
                for idx in mode_indices[sub]:
                    schedule[idx, t] = 0  # Turn off other modes of the same subsystem
                schedule[mode_idx, t] = 1  # Activate the selected mode
    
    return schedule

def write_schedule(schedule, mode_list, filename="power_schedule.csv", time_step=2):
    """Writes the generated schedule to a CSV file."""
    time_slots = schedule.shape[1]
    
    with open(filename, mode="w", newline="") as file:
        writer = csv.writer(file)
        header = ["Time (min)"] + [f"{mode['subsystem']} - {mode['mode']}" for mode in mode_list] + ["Total Power (W)"]
        writer.writerow(header)
        
        for t in range(time_slots):
            time = t * time_step
            states = schedule[:, t]
            total_power = sum(states[i] * mode_list[i]["power"] for i in range(len(states)))
            writer.writerow([time] + list(states) + [total_power])

def main():
    subsystems, mode_list, mode_indices = read_power_table("subsystem_power_table.csv")
    schedule = generate_schedule(subsystems, mode_list, mode_indices)
    write_schedule(schedule, mode_list, time_step=1)
    print("Power schedule generated and saved to power_schedule.csv.")

if __name__ == "__main__":
    main()