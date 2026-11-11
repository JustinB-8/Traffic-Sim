from drafter import *
from dataclasses import dataclass
from PIL import Image as PILImage
from PIL import ImageDraw
import math



hide_debug_information()
set_website_title("Traffic Simulator")
set_website_framed(False)


# ==========================================
# DATACLASSES
# ==========================================

@dataclass
class Vehicle:
    """Represents one vehicle in the traffic simulation.

    Stores the vehicle's ID, position, speed, direction,
    and whether it is waiting in traffic.
    """
    vehicle_id: int
    position: int
    speed: int
    direction: str
    waiting: bool


@dataclass
class State:
    """Stores the current settings and progress of the website.

    Keeps track of the intersection type, traffic density,
    vehicles, simulation status, speed, steps, and
    traffic statistics.
    """
    intersection_type: str
    traffic_density: int
    vehicles: list[Vehicle]
    simulation_running: bool
    simulation_step: int
    vehicle_speed: int
    simulation_completed: bool
    total_waiting_time: int
    maximum_waiting: int


# ==========================================
# HELPER FUNCTIONS
# ==========================================

def density_name(density: int) -> str:
    """Converts the traffic density number into its name.

    1 represents Low, 2 represents Medium, and 3 represents High.
    Returns the density as a string.
    """
    if density == 1:
        return "Low"
    elif density == 2:
        return "Medium"
    else:
        return "High"


def speed_name(speed: int) -> str:
    """Converts the vehicle speed number into its name.

    1 represents Slow, 2 represents Normal, and 3 represents Fast.
    Returns the speed as a string.
    """
    if speed == 1:
        return "Slow"
    elif speed == 2:
        return "Normal"
    else:
        return "Fast"


def reset_data(state: State):
    """Resets the simulation without changing the user's settings.

    Removes all vehicles and resets the simulation status,
    step counter, and waiting statistics.
    """
    state.vehicles = []
    state.simulation_running = False
    state.simulation_completed = False
    state.simulation_step = 0
    state.total_waiting_time = 0
    state.maximum_waiting = 0


def create_vehicles(state: State):
    """Creates vehicles based on the selected traffic density.

    Generates 4, 8, or 12 vehicles depending on the density.
    Assigns each vehicle an ID, direction, starting position,
    and speed, then adds it to the State's vehicles list.
    """
    state.vehicles = []

    if state.traffic_density == 1:
        amount = 4
    elif state.traffic_density == 2:
        amount = 8
    else:
        amount = 12

    if state.intersection_type == "T-Intersection":
        directions = ["South", "East", "West"]
    else:
        directions = ["North", "South", "East", "West"]

    for i in range(amount):
        direction = directions[i % len(directions)]
        row = i // len(directions)

        vehicle = Vehicle(
            i + 1,
            -row * 3,
            state.vehicle_speed,
            direction,
            False
        )

        state.vehicles.append(vehicle)


# ==========================================
# DRAWING THE ROADS
# ==========================================

def draw_roads(draw, intersection_type: str):
    """Draws the selected intersection layout.

    Uses Pillow to draw the roads, lane markings, and
    direction labels for a four-way intersection,
    T-intersection, or roundabout.
    """
    grass = "#79A96B"
    road = "#41464C"
    yellow = "#F4E6A0"
    white = "#FFFFFF"

    if intersection_type == "Four-Way":
        draw.rectangle((255, 0, 345, 500), fill=road)
        draw.rectangle((0, 205, 600, 295), fill=road)

        draw.line((300, 0, 300, 205),
                  fill=yellow, width=3)
        draw.line((300, 295, 300, 500),
                  fill=yellow, width=3)
        draw.line((0, 250, 255, 250),
                  fill=yellow, width=3)
        draw.line((345, 250, 600, 250),
                  fill=yellow, width=3)

        draw.line((255, 190, 300, 190),
                  fill=white, width=4)
        draw.line((300, 310, 345, 310),
                  fill=white, width=4)
        draw.line((240, 250, 240, 295),
                  fill=white, width=4)
        draw.line((360, 205, 360, 250),
                  fill=white, width=4)

    elif intersection_type == "T-Intersection":
        draw.rectangle((0, 205, 600, 295), fill=road)
        draw.rectangle((255, 250, 345, 500), fill=road)

        draw.line((0, 250, 255, 250),
                  fill=yellow, width=3)
        draw.line((345, 250, 600, 250),
                  fill=yellow, width=3)
        draw.line((300, 295, 300, 500),
                  fill=yellow, width=3)

        draw.line((300, 310, 345, 310),
                  fill=white, width=4)

    elif intersection_type == "Roundabout":
        draw.rectangle((255, 0, 345, 500), fill=road)
        draw.rectangle((0, 205, 600, 295), fill=road)

        draw.ellipse((185, 135, 415, 365),
                     fill=road)

        draw.ellipse((245, 195, 355, 305),
                     fill=grass)

        draw.ellipse((245, 195, 355, 305),
                     outline=white, width=3)

        draw.arc((215, 165, 385, 335),
                 0, 359, fill=yellow, width=2)

    if intersection_type != "T-Intersection":
        draw.text((355, 20), "NORTH", fill="black")

    draw.text((15, 175), "WEST", fill="black")
    draw.text((520, 175), "EAST", fill="black")
    draw.text((355, 465), "SOUTH", fill="black")


# ==========================================
# VEHICLE COORDINATES
# ==========================================

def vehicle_coordinates(vehicle: Vehicle,
                        intersection_type: str):
    """Calculates where a vehicle should appear in the image.

    Uses the vehicle's position, direction, and intersection
    type to calculate its x and y coordinates.
    Returns the coordinates and vehicle orientation.
    """

    position = vehicle.position

    if intersection_type == "Roundabout":
        # Approach the circular roadway.
        if position < 6:
            distance = (position + 3) * 17

            if vehicle.direction == "North":
                return (322, 20 + distance, "vertical")
            elif vehicle.direction == "South":
                return (278, 480 - distance, "vertical")
            elif vehicle.direction == "West":
                return (20 + distance, 272, "horizontal")
            else:
                return (580 - distance, 228, "horizontal")

        # Move around the circle.
        if vehicle.direction == "North":
            start_angle = -math.pi / 2
        elif vehicle.direction == "South":
            start_angle = math.pi / 2
        elif vehicle.direction == "West":
            start_angle = math.pi
        else:
            start_angle = 0

        angle = start_angle + (position - 6) * 0.35

        x = 300 + 85 * math.cos(angle)
        y = 250 + 85 * math.sin(angle)

        return (x, y, "horizontal")

    # Four-way and T-intersection.
    distance = (position + 3) * 17

    if vehicle.direction == "North":
        return (322, 20 + distance, "vertical")
    elif vehicle.direction == "South":
        return (278, 480 - distance, "vertical")
    elif vehicle.direction == "West":
        return (20 + distance, 272, "horizontal")
    else:
        return (580 - distance, 228, "horizontal")


# ==========================================
# DRAW VEHICLES
# ==========================================

def draw_vehicle(draw, vehicle: Vehicle,
                 intersection_type: str):
    """Draws an individual vehicle on the intersection image.

    Uses the vehicle's coordinates to draw a numbered car.
    Moving vehicles are blue and waiting vehicles are red.
    Vehicles that have completed their route are not drawn.
    """

    if vehicle.position >= 12:
        return

    x, y, orientation = vehicle_coordinates(
        vehicle, intersection_type
    )

    if vehicle.waiting:
        color = "#E74C3C"
    else:
        color = "#3498DB"

    if orientation == "vertical":
        draw.rounded_rectangle(
            (x - 10, y - 17, x + 10, y + 17),
            radius=4,
            fill=color,
            outline="black",
            width=2
        )
        draw.rectangle(
            (x - 7, y - 8, x + 7, y - 2),
            fill="#BDE6F4"
        )
    else:
        draw.rounded_rectangle(
            (x - 17, y - 10, x + 17, y + 10),
            radius=4,
            fill=color,
            outline="black",
            width=2
        )
        draw.rectangle(
            (x - 6, y - 7, x, y + 7),
            fill="#BDE6F4"
        )

    draw.text(
        (x - 4, y - 5),
        str(vehicle.vehicle_id),
        fill="white"
    )


def draw_intersection(state: State):
    picture = PILImage.new(
        "RGB", (600, 500), "#79A96B"
    )

    draw = ImageDraw.Draw(picture)

    draw_roads(draw, state.intersection_type)

    for vehicle in state.vehicles:
        draw_vehicle(
            draw,
            vehicle,
            state.intersection_type
        )

    return picture


# ==========================================
# TRAFFIC MOVEMENT
# ==========================================

def move_vehicles(state: State):
    """Advances every vehicle by one simulation step.

    Loops through vehicles and updates their positions based
    on their speed. Checks for vehicles ahead and whether
    the intersection is occupied to prevent some conflicts.
    Records the total and maximum number of waiting vehicles.
    """
    # Vehicles move toward position 12.
    # Positions 6-8 represent the intersection.
    # One new vehicle may enter the center
    # during each step.

    center_occupied = False

    for vehicle in state.vehicles:
        if 6 <= vehicle.position < 9:
            center_occupied = True

    center_reserved = center_occupied

    # Vehicles nearest the exit move first.
    ordered = sorted(
        state.vehicles,
        key=lambda car: car.position,
        reverse=True
    )

    waiting_this_step = 0

    for vehicle in ordered:
        if vehicle.position >= 12:
            vehicle.waiting = False
            continue

        old_position = vehicle.position
        new_position = old_position + vehicle.speed

        if new_position > 12:
            new_position = 12

        # Prevent cars from passing others
        # traveling in the same direction.
        for other in state.vehicles:
            if other.vehicle_id != vehicle.vehicle_id:
                if other.direction == vehicle.direction:
                    if old_position < other.position < 12:
                        safe_position = other.position - 2

                        if new_position > safe_position:
                            new_position = safe_position

        # Stop at position 5 if the center
        # is occupied or already reserved.
        if old_position < 6 and new_position >= 6:
            if center_reserved:
                new_position = 5
            else:
                center_reserved = True

        # A vehicle must not move backward.
        if new_position < old_position:
            new_position = old_position

        vehicle.position = new_position

        if new_position == old_position:
            vehicle.waiting = True
            waiting_this_step += 1
        else:
            vehicle.waiting = False

    # Record waiting statistics.
    state.total_waiting_time += waiting_this_step

    if waiting_this_step > state.maximum_waiting:
        state.maximum_waiting = waiting_this_step


# ==========================================
# STATISTICS
# ==========================================

def calculate_results(state: State):
    """Calculates statistics from the current simulation.

    Counts moving, waiting, and completed vehicles.
    Calculates the completion rate, average delay,
    throughput, and congestion level.
    Returns a list of strings containing the statistics.
    """
    moving = 0
    waiting = 0
    completed = 0

    for vehicle in state.vehicles:
        if vehicle.position >= 12:
            completed += 1
        elif vehicle.waiting:
            waiting += 1
        else:
            moving += 1

    total = len(state.vehicles)

    if total > 0:
        completion_rate = round(
            completed / total * 100, 1
        )

        average_delay = round(
            state.total_waiting_time / total, 2
        )
    else:
        completion_rate = 0
        average_delay = 0

    if state.simulation_step > 0:
        throughput = round(
            completed / state.simulation_step, 2
        )
    else:
        throughput = 0

    if average_delay < 2:
        congestion_level = "Low"
    elif average_delay < 5:
        congestion_level = "Moderate"
    else:
        congestion_level = "High"

    return [
        "Total Vehicles: " + str(total),
        "Completed Vehicles: " + str(completed),
        "Moving Vehicles: " + str(moving),
        "Waiting Vehicles: " + str(waiting),
        "Completion Rate: " + str(completion_rate) + "%",
        "Total Simulation Steps: " + str(state.simulation_step),
        "Total Waiting Time: " +
        str(state.total_waiting_time) + " vehicle-steps",
        "Average Delay Per Vehicle: " +
        str(average_delay) + " steps",
        "Maximum Vehicles Waiting at Once: " +
        str(state.maximum_waiting),
        "Throughput: " +
        str(throughput) + " vehicles per step",
        "Congestion Level: " + congestion_level
    ]


# ==========================================
# PAGE 1 - HOME
# ==========================================

@route
def index(state: State) -> Page:
    """Displays the homepage of the Traffic Flow Simulator.

    Explains the purpose of the website, lists the available
    intersections, and provides a button to begin.
    Returns the homepage as a Drafter Page.
    """
    return Page(state, [
        Header("Traffic Flow Simulator"),

        "Welcome to the Traffic Flow Simulator!",

        "Explore how vehicles move through "
        "different types of intersections.",

        "Choose an intersection, adjust traffic "
        "density and speed, and observe congestion.",

        Header("Available Intersections"),

        "Four-Way Intersection",
        "T-Intersection",
        "Roundabout",

        Button("Begin Simulation", "choose_intersection")
    ])


# ==========================================
# PAGE 2 - CHOOSE INTERSECTION
# ==========================================

@route
def choose_intersection(state: State) -> Page:
    """Displays the intersection selection page.

    Allows the user to choose a four-way intersection,
    T-intersection, or roundabout using a dropdown menu.
    Returns the selection page.
    """
    return Page(state, [
        Header("Choose an Intersection"),

        "Select the intersection you want to study.",

        SelectBox(
            "intersection_choice",
            ["Four-Way", "T-Intersection", "Roundabout"],
            state.intersection_type
        ),

        Button("Continue", "save_intersection"),
        Button("Home", "index")
    ])


@route
def save_intersection(
        state: State,
        intersection_choice: str) -> Page:
    """Saves the user's selected intersection type.

    Updates the State with the chosen intersection,
    resets the previous simulation, and opens
    the traffic settings page.
    """

    state.intersection_type = intersection_choice
    reset_data(state)

    return set_traffic(state)


# ==========================================
# PAGE 3 - TRAFFIC SETTINGS
# ==========================================

@route
def set_traffic(state: State) -> Page:
    """Displays the traffic settings page.

    Allows the user to choose traffic density and
    vehicle speed using dropdown menus.
    Returns the traffic settings page.
    """
    return Page(state, [
        Header("Traffic Settings"),

        "Intersection: " + state.intersection_type,

        "Traffic Density:",

        SelectBox(
            "density_choice",
            ["Low", "Medium", "High"],
            density_name(state.traffic_density)
        ),

        "Vehicle Speed:",

        SelectBox(
            "speed_choice",
            ["Slow", "Normal", "Fast"],
            speed_name(state.vehicle_speed)
        ),

        Button("Save Settings", "save_traffic"),
        Button("Back", "choose_intersection")
    ])


@route
def save_traffic(
        state: State,
        density_choice: str,
        speed_choice: str) -> Page:
    """Saves the user's traffic density and speed settings.

    Converts the selected names into integer values,
    updates the State, resets the simulation, and
    opens the simulation page.
    """

    if density_choice == "Low":
        state.traffic_density = 1
    elif density_choice == "Medium":
        state.traffic_density = 2
    else:
        state.traffic_density = 3

    if speed_choice == "Slow":
        state.vehicle_speed = 1
    elif speed_choice == "Normal":
        state.vehicle_speed = 2
    else:
        state.vehicle_speed = 3

    reset_data(state)

    return simulation(state)


# ==========================================
# PAGE 4 - SIMULATION
# ==========================================

@route
def simulation(state: State) -> Page:
    """Displays the traffic simulation page.

    Shows the selected settings, simulation status,
    current step, and overhead intersection image.
    Provides buttons to start, advance, reset,
    and navigate to other pages.
    Returns the simulation page.
    """

    content = [
        Header("Traffic Simulation"),

        "Intersection: " + state.intersection_type,

        "Traffic Density: " +
        density_name(state.traffic_density),

        "Vehicle Speed: " +
        speed_name(state.vehicle_speed),

        "Simulation Step: " +
        str(state.simulation_step)
    ]

    # Keep the main button above the picture.
    if state.simulation_completed:
        content.append("SIMULATION COMPLETE!")

        content.append(
            Button("View Final Results", "results")
        )

    elif state.simulation_running:
        content.append("Status: RUNNING")

        content.append(
            Button("Advance Simulation", "advance_simulation")
        )

    else:
        content.append("Status: READY")

        content.append(
            Button("Start Simulation", "start_simulation")
        )

    content += [
        Button("Reset Simulation", "reset_simulation"),
        Button("View Results", "results"),
        Button("Change Settings", "set_traffic"),
        Button("Home", "index"),

        Header("Intersection Visualization"),

        Image(
            draw_intersection(state),
            600,
            500,
            alt="Overhead traffic intersection simulation"
        ),

        "Blue = Moving Vehicles",
        "Red = Waiting Vehicles"
    ]

    return Page(state, content)


# ==========================================
# START SIMULATION
# ==========================================

@route
def start_simulation(state: State) -> Page:
    """Starts a new traffic simulation.

    Resets previous simulation data, creates vehicles
    based on the selected settings, and changes the
    simulation status to running.
    Returns the updated simulation page.
    """

    reset_data(state)

    create_vehicles(state)

    state.simulation_running = True

    return simulation(state)


# ==========================================
# ADVANCE SIMULATION
# ==========================================

@route
def advance_simulation(state: State) -> Page:
    """Advances the traffic simulation by one step.

    Moves vehicles and increases the step counter
    when the simulation is running. Checks whether
    all vehicles have finished and marks the
    simulation complete when they have.
    Returns the updated simulation page.
    """

    if state.simulation_running:
        move_vehicles(state)

        state.simulation_step += 1

        all_finished = True

        for vehicle in state.vehicles:
            if vehicle.position < 12:
                all_finished = False

        if all_finished:
            state.simulation_running = False
            state.simulation_completed = True

    return simulation(state)


# ==========================================
# RESET SIMULATION
# ==========================================

@route
def reset_simulation(state: State) -> Page:
    """Resets the current traffic simulation.

    Clears the vehicles, step counter, completion
    status, and traffic statistics while keeping
    the user's intersection and traffic settings.
    Returns the reset simulation page.
    """

    reset_data(state)

    return simulation(state)


# ==========================================
# PAGE 5 - RESULTS
# ==========================================

@route
def results(state: State) -> Page:
    """Displays the simulation results page.

    Shows the selected settings and calculated traffic
    statistics. If the simulation is complete, it also
    provides an analysis of the congestion level.
    Returns the results page.
    """

    content = [
        Header("Traffic Simulation Results"),

        "Intersection: " + state.intersection_type,

        "Traffic Density: " +
        density_name(state.traffic_density),

        "Vehicle Speed: " +
        speed_name(state.vehicle_speed)
    ]

    if state.simulation_completed:
        content.append(
            Header("Simulation Successfully Completed!")
        )
        content.append(
            "All vehicles have exited the intersection."
        )

    elif state.simulation_running:
        content.append(
            "Simulation is still running. "
            "These are the current statistics."
        )

    else:
        content.append(
            "Start a simulation to generate results."
        )

    content.append(Header("Traffic Statistics"))

    statistics = calculate_results(state)

    for statistic in statistics:
        content.append(statistic)

    if state.simulation_completed:
        content.append(Header("Final Analysis"))

        average_delay = 0

        if len(state.vehicles) > 0:
            average_delay = (
                state.total_waiting_time /
                len(state.vehicles)
            )

        if average_delay < 2:
            content.append(
                "Traffic flowed efficiently through "
                "the intersection with minimal delays."
            )

        elif average_delay < 5:
            content.append(
                "The intersection experienced moderate "
                "congestion and some vehicle delays."
            )

        else:
            content.append(
                "The intersection experienced high "
                "congestion and significant delays."
            )

        content.append(
            "Try changing the intersection type, "
            "traffic density, or vehicle speed to "
            "compare the results."
        )

    content += [
        Button("Return to Simulation", "simulation"),
        Button("Reset Simulation", "reset_simulation"),
        Button("Change Intersection", "choose_intersection"),
        Button("Home", "index")
    ]

    return Page(state, content)


# ==========================================
# START WEBSITE
# ==========================================

initial_state = State(
    "Four-Way",
    1,
    [],
    False,
    0,
    2,
    False,
    0,
    0
)

start_server(
    initial_state,
    site_title="Traffic Flow Simulator"
)


