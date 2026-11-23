# Transit System - Distributed Transit Scheduling

## Project Overview

For this project, we developed a distributed transit system using Python, RabbitMQ, and Docker. The main goal was to simulate a public transit network where buses are tracked in real time and schedules automatically adjust based on passenger demand.

We used routes around the Oshawa and Durham Region area to make the simulation more realistic. Instead of having buses follow the same schedule all day, our system can increase or decrease bus frequency depending on how busy a route is.

We also created a passenger interface that displays bus locations, routes, estimated arrival times, and current schedules on a map.

## Technologies Used

- **Python** – Used to develop the different services and simulation logic.
- **PyCharm** – Our main development environment.
- **RabbitMQ** – Allows the services to communicate by sending and receiving messages.
- **Docker and Docker Compose** – Runs the services in separate containers.
- **FastAPI and Uvicorn** – Used to run the passenger interface server.
- **HTML and JavaScript** – Used to create the passenger interface and display transit information.

## How the System Works

Our project is divided into several services that work together.

### 1. Vehicle Tracking Service

The vehicle tracking service simulates buses travelling along different routes. It updates their GPS coordinates, speed, passenger occupancy, and next stop.

This information is sent through RabbitMQ so other services can receive the latest bus locations.

### 2. Demand Service

The demand service simulates passenger activity throughout the day.

Passenger demand changes depending on the time, with higher demand during morning and evening rush hours and lower demand during quieter periods.

The service classifies demand as PEAK, NORMAL, or OFF_PEAK.

### 3. Scheduling Service

The scheduling service receives demand updates and adjusts bus schedules accordingly.

The system currently uses:

- PEAK: A bus every 5 minutes.
- NORMAL: A bus every 10 minutes.
- OFF_PEAK: A bus every 20 minutes.

The number of buses assigned to each route is calculated based on the route length and required frequency.

### 4. Passenger Interface

We created a web interface that allows passengers to view the transit system on a map.

The interface displays bus locations, transit routes, estimated arrival times, and current schedules. It regularly updates the information so passengers can see changes as the simulation runs.

### 5. RabbitMQ Communication

RabbitMQ connects the different services.

Instead of having every service directly communicate with another, messages are published through RabbitMQ and received by whichever service needs them.

This makes the project easier to organize and allows the services to operate independently.

## Project Structure

```text
transit-system/
│
├── common/
│   ├── bus.py
│   ├── messages.py
│   └── routes.py
│
├── vehicle_tracking/
│   └── tracking.py
│
├── demand_service/
│   └── demand.py
│
├── scheduling_service/
│   └── scheduling.py
│
├── passenger_interface/
│   ├── eta.py
│   ├── server.py
│   └── index.html
│
├── evaluation/
│   ├── measure_latency.py
│   ├── compare_scheduling.py
│   ├── latency_results.csv
│   └── scheduling_results.csv
│
├── Dockerfile
├── docker-compose.yml
├── requirements.txt
├── .dockerignore
├── test_send.py
└── test_receive.py
```

## How to Run the Project

### Step 1: Install the Required Software

Before running the project, make sure you have:

- Python installed
- Docker Desktop installed and running
- PyCharm or another code editor

### Step 2: Open the Project

Download or clone the project and open the `transit-system` folder in PyCharm.

```bash
git clone https://github.com/hashir-rashid/transit-distributed-project.git@latest
cd transit-system
```

Make sure the folder contains the `docker-compose.yml` file.

### Step 3: Start the Services

Run the following command:

```bash
docker compose up --build -d
```

This builds and starts the containers for RabbitMQ, vehicle tracking, passenger demand, scheduling, and the passenger interface.

### Step 4: Check the Containers

To check that everything is running, enter:

```bash
docker compose ps
```

You should see the five services running.

### Step 5: Open the Passenger Interface

Open a browser and visit:

http://localhost:8000

You should see the transit map with the simulated routes and bus locations.

### Step 6: View Service Logs

You can check the output of individual services using:

```bash
docker compose logs --tail=30 vehicle_tracking
```

```bash
docker compose logs --tail=30 demand_service
```

```bash
docker compose logs --tail=30 scheduling_service
```

### Step 7: Stop the System

When finished, run:

```bash
docker compose down
```

This stops and removes the project's containers.

## Viewing Individual Services

If you want to check what each service is doing without looking at the entire system, you can view its output separately through the PyCharm terminal.

First, make sure Docker Desktop is running and start the system using:

```bash
docker compose up --build -d
```

Once everything is running, use the following commands to view each service:

**1. Vehicle Tracking Service**

Shows the buses moving along their routes, including their GPS locations and passenger counts.

```bash
docker compose logs -f vehicle_tracking
```

**2. Demand Service**

Shows how many passengers are using each route and whether demand is NORMAL, PEAK, or OFF_PEAK.

```bash
docker compose logs -f demand_service
```

**3. Scheduling Service**

Shows how bus schedules change based on passenger demand, including how often buses arrive and how many buses are assigned.

```bash
docker compose logs -f scheduling_service
```

**4. Passenger Interface**

Shows the server activity for the passenger interface.

```bash
docker compose logs -f passenger_interface
```

To view the actual passenger interface and live bus map, open your browser and go to:

http://localhost:8000

**5. RabbitMQ**

RabbitMQ handles communication between the different services. To check its logs, run:

```bash
docker compose logs -f rabbitmq
```

You can also open the RabbitMQ management dashboard at:

http://localhost:15672

Use the RabbitMQ login credentials configured for the project (found in the .env file).

### Additional Commands

To check which containers are running:

```bash
docker compose ps
```

To view the latest 30 log messages from a specific service:

```bash
docker compose logs --tail=30 scheduling_service
```

To stop watching a service's logs, press **Ctrl + C**. This only stops the log viewer, not the Docker container.

To stop the entire system:

```bash
docker compose down
```

Each group member can use these commands to focus on their assigned service without having to go through all the other services' outputs.

## Testing and Evaluation

We performed several tests to check that the services were communicating properly and that the scheduling system was working as expected.

### RabbitMQ Communication Testing

We used `test_send.py` and `test_receive.py` to confirm that messages could be published and received successfully.

We also tested the vehicle tracking service and confirmed that bus locations and passenger occupancy were updating continuously.

### Latency Testing

We created `measure_latency.py` to measure how long messages take to travel through the system.

The results are saved in `evaluation/latency_results.csv` for analysis.

### Fixed vs. Dynamic Scheduling

We also compared our dynamic scheduling system against a traditional fixed schedule.

For the comparison, fixed scheduling used a bus frequency of 10 minutes, while dynamic scheduling adjusted its frequency based on demand.

Our results showed:

| Demand Level | Fixed Wait | Dynamic Wait | Difference |
|---|---|---|---|
| OFF_PEAK | 5 minutes | 10 minutes | 100% longer |
| NORMAL | 5 minutes | 5 minutes | No change |
| PEAK | 5 minutes | 2.5 minutes | 50% reduction |

These are calculated average waiting times based on the bus frequency.

During peak hours, dynamic scheduling reduced the expected average passenger waiting time by 50%. During quieter periods, the system reduced the number of buses assigned to routes, although this increased waiting times.

The results are saved in `evaluation/scheduling_results.csv`.

To run the comparison:

```bash
python evaluation/compare_scheduling.py
```

## Challenges We Faced

One of the main challenges was getting the different services to communicate properly. Since each service runs independently, we needed to make sure messages were being sent and received correctly through RabbitMQ.

We also had some issues setting up Docker and accessing the passenger interface through localhost. We worked through these problems by checking container statuses, reviewing service logs, and testing the API.

Another challenge was making sure the bus simulation and scheduling system worked together. We tested the services separately before running the complete system.

## Conclusion

Overall, we were able to build a working distributed transit simulation where multiple services communicate through RabbitMQ.

Our system can simulate moving buses, track passenger demand, adjust schedules, and display transit information through a web interface.

The scheduling comparison also demonstrated how dynamic scheduling can improve expected passenger waiting times during busy periods while reducing the number of buses needed during quieter hours.


This project helped us better understand distributed systems, message-based communication, Docker containers, and how different services can work together in a real-world application.
