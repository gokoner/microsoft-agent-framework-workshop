
"""
Travel Booking MCP Server
A FastMCP server that provides travel-related tools for AI agents
"""

from fastmcp import FastMCP
from datetime import datetime, timedelta
from typing import List, Optional, Dict
from pydantic import BaseModel, Field
import random

# Initialize the MCP server
mcp = FastMCP("Travel Booking Server")

# Data models for structured responses
class Flight(BaseModel):
    """Flight information"""
    flight_number: str
    airline: str
    departure: str
    arrival: str
    departure_time: str
    arrival_time: str
    price: float
    currency: str = "USD"
    available_seats: int

class Hotel(BaseModel):
    """Hotel information"""
    hotel_name: str
    location: str
    room_type: str
    price_per_night: float
    currency: str = "USD"
    available_rooms: int
    amenities: List[str]

# Underlying functions that return JSON-serializable data
def _search_flights(
    origin: str,
    destination: str,
    departure_date: str,
    passengers: int = 1
) -> List[Dict]:
    """
    Search for available flights between two cities.

    Args:
        origin: Departure city (e.g., "New York", "NYC")
        destination: Arrival city (e.g., "London", "LHR")
        departure_date: Date in YYYY-MM-DD format
        passengers: Number of passengers (default: 1)

    Returns:
        List of available flights with details (as dicts)
    """
    # Simulate flight search (in production, call real APIs)
    airlines = ["Delta", "United", "American", "British Airways"]

    flights = []
    for i in range(3):
        dep_time = datetime.strptime(departure_date, "%Y-%m-%d")
        dep_time = dep_time.replace(hour=random.randint(6, 20), minute=random.choice([0, 15, 30, 45]))
        arr_time = dep_time + timedelta(hours=random.randint(6, 12))

        flight = {
            "flight_number": f"{random.choice(['DL', 'UA', 'AA', 'BA'])}{random.randint(100, 999)}",
            "airline": random.choice(airlines),
            "departure": origin,
            "arrival": destination,
            "departure_time": dep_time.strftime("%Y-%m-%d %H:%M"),
            "arrival_time": arr_time.strftime("%Y-%m-%d %H:%M"),
            "price": round(random.uniform(300, 1200), 2),
            "currency": "USD",
            "available_seats": random.randint(5, 50)
        }
        flights.append(flight)

    return flights

def _check_hotel_availability(
    location: str,
    check_in: str,
    check_out: str,
    guests: int = 2
) -> List[Dict]:
    """
    Check hotel room availability in a specific location.

    Args:
        location: City or area name
        check_in: Check-in date in YYYY-MM-DD format
        check_out: Check-out date in YYYY-MM-DD format
        guests: Number of guests (default: 2)

    Returns:
        List of available hotels with details (as dicts)
    """
    # Simulate hotel search (in production, call real APIs)
    hotel_names = ["Grand Plaza Hotel", "Seaside Resort", "Downtown Suites", "Airport Inn"]
    room_types = ["Standard Room", "Deluxe Room", "Suite", "Executive Suite"]

    hotels = []
    for i in range(4):
        hotel = {
            "hotel_name": random.choice(hotel_names),
            "location": location,
            "room_type": random.choice(room_types),
            "price_per_night": round(random.uniform(80, 350), 2),
            "currency": "USD",
            "available_rooms": random.randint(1, 10),
            "amenities": random.sample(["WiFi", "Pool", "Gym", "Restaurant", "Spa", "Parking"], k=3)
        }
        hotels.append(hotel)

    return hotels

def _convert_currency(
    amount: float,
    from_currency: str,
    to_currency: str
) -> Dict:
    """
    Convert amount from one currency to another.

    Args:
        amount: Amount to convert
        from_currency: Source currency code (e.g., "USD", "EUR", "GBP")
        to_currency: Target currency code

    Returns:
        Dictionary with conversion details
    """
    # Simulate currency conversion (in production, call real exchange rate API)
    exchange_rates = {
        "USD": {"EUR": 0.85, "GBP": 0.73, "JPY": 110.0, "USD": 1.0},
        "EUR": {"USD": 1.18, "GBP": 0.86, "JPY": 129.0, "EUR": 1.0},
        "GBP": {"USD": 1.37, "EUR": 1.16, "JPY": 150.0, "GBP": 1.0},
        "JPY": {"USD": 0.0091, "EUR": 0.0078, "GBP": 0.0067, "JPY": 1.0}
    }

    rate = exchange_rates.get(from_currency, {}).get(to_currency, 1.0)
    converted_amount = round(amount * rate, 2)

    return {
        "original_amount": amount,
        "original_currency": from_currency,
        "converted_amount": converted_amount,
        "converted_currency": to_currency,
        "exchange_rate": rate,
        "timestamp": datetime.now().isoformat()
    }

def _get_server_info() -> Dict:
    """Get information about this MCP server"""
    return {
        "name": "Travel Booking Server",
        "version": "1.0.0",
        "tools": ["search_flights", "check_hotel_availability", "convert_currency"],
        "description": "MCP server for travel booking operations"
    }

# MCP tool wrappers - convert results to Pydantic models for MCP
@mcp.tool()
def search_flights(
    origin: str,
    destination: str,
    departure_date: str,
    passengers: int = 1
) -> List[Flight]:
    """
    Search for available flights between two cities.

    Args:
        origin: Departure city (e.g., "New York", "NYC")
        destination: Arrival city (e.g., "London", "LHR")
        departure_date: Date in YYYY-MM-DD format
        passengers: Number of passengers (default: 1)

    Returns:
        List of available flights with details
    """
    flights_data = _search_flights(origin, destination, departure_date, passengers)
    return [Flight(**f) for f in flights_data]

@mcp.tool()
def check_hotel_availability(
    location: str,
    check_in: str,
    check_out: str,
    guests: int = 2
) -> List[Hotel]:
    """
    Check hotel room availability in a specific location.

    Args:
        location: City or area name
        check_in: Check-in date in YYYY-MM-DD format
        check_out: Check-out date in YYYY-MM-DD format
        guests: Number of guests (default: 2)

    Returns:
        List of available hotels with details
    """
    hotels_data = _check_hotel_availability(location, check_in, check_out, guests)
    return [Hotel(**h) for h in hotels_data]

@mcp.tool()
def convert_currency(
    amount: float,
    from_currency: str,
    to_currency: str
) -> dict:
    """
    Convert amount from one currency to another.

    Args:
        amount: Amount to convert
        from_currency: Source currency code (e.g., "USD", "EUR", "GBP")
        to_currency: Target currency code

    Returns:
        Dictionary with conversion details
    """
    return _convert_currency(amount, from_currency, to_currency)

@mcp.tool()
def get_server_info() -> dict:
    """Get information about this MCP server"""
    return _get_server_info()

# ASGI app for uvicorn (used in container deployment - Tutorial 16)
# Uses simple HTTP transport (NOT streamable-http which requires SSE) with STATELESS mode
# for Azure Foundry Agent Service compatibility
# Ref: https://learn.microsoft.com/en-us/azure/ai-foundry/agents/how-to/mcp-authentication
# "State | Stateless only" - Foundry requires MCP servers to be stateless
# transport="http" = simple JSON-RPC over HTTP without SSE (streamable-http is default but needs SSE)
app = mcp.http_app(transport="http", stateless_http=True)

if __name__ == "__main__":
    # Run the server locally via stdio transport
    mcp.run()
