import csv
import numpy as np

# Much of this is GPT generated - it works, but there may be much cleaner ways
# this stuff

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
    
def generate_schedule(subsystems, mode_list, orbit_duration=90, time_step=2):
    """Generates a schedule ensuring correct duty cycles and balanced power consumption."""
    time_slots = orbit_duration // time_step
    schedule = np.zeros((len(mode_list), time_slots), dtype=int)
    
    # Dictionary to track which time slots are used by each subsystem
    subsystem_active_slots = {sub: set() for sub in subsystems}

    for sub, modes in subsystems.items():
        available_slots = list(range(time_slots))  # Create a list of all available time slots
        np.random.shuffle(available_slots)  # Shuffle to distribute load
        
        for mode in modes:
            active_slots = int(mode["duty_cycle"] * time_slots)  # Number of slots this mode should be active
            mode_index = mode_list.index(mode)

            # Ensure that we do not overlap modes for the same subsystem
            selected_slots = []
            for slot in available_slots:
                if len(selected_slots) >= active_slots:
                    break
                if slot not in subsystem_active_slots[sub]:  # Ensure no overlap
                    selected_slots.append(slot)
                    subsystem_active_slots[sub].add(slot)  # Mark slot as used for this subsystem
            
            selected_slots.sort()  # Sort to keep chronological order
            for t in selected_slots:
                schedule[mode_index, t] = 1  # Activate the mode at the chosen time slot

            # Remove selected slots from available pool
            available_slots = [slot for slot in available_slots if slot not in selected_slots]

    return schedule

def write_schedule(schedule, mode_list, filename="power_schedule.csv", time_step=2):
    """Writes the generated schedule to a CSV file."""
    time_slots = schedule.shape[1]
    
    with open(filename, mode="w", newline="") as file:
        writer = csv.writer(file)
        header = ["Time (min)"] + [f"{mode['subsystem']} - {mode['mode']}" for mode in mode_list] + ["Total Power (W)", "Net Discharge Current (A)"]
        writer.writerow(header)
        
        for t in range(time_slots):
            time = t * time_step
            states = schedule[:, t]
            total_power = sum(states[i] * mode_list[i]["power"] for i in range(len(states)))
            net_discharge_current = sum(states[i] * mode_list[i]["current"] for i in range(len(states)))
            writer.writerow([time] + list(states) + [total_power, net_discharge_current])

def main():
    subsystems, mode_list, mode_indices = read_power_table("Pack Model V1/subsystem_power_table.csv")
    schedule = generate_schedule(subsystems, mode_list, time_step=1)
    write_schedule(schedule, mode_list, time_step=1)
    print("Power schedule generated and saved to power_schedule.csv.")

if __name__ == "__main__":
    main()