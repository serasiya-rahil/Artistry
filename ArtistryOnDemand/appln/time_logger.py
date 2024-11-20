import os
import time
import logging
from .Debug import *
import xml.etree.ElementTree as ET
from xml.dom import minidom

dbg = SimpleDebugger(enabled=True)

STATS_FILE = "global_stats.xml"

# Initialize or load global stats
def load_global_stats():
    """Load stats from an XML file or initialize if unavailable."""
    if os.path.exists(STATS_FILE):
        try:
            tree = ET.parse(STATS_FILE)
            root = tree.getroot()
            total_time = float(root.find("total_time").text)
            count = int(root.find("count").text)

            # Safely load current_avg with a default value if missing or invalid
            current_avg_elem = root.find("current_avg")
            current_avg = 0.0  # Default value if missing or invalid
            if current_avg_elem is not None:
                try:
                    current_avg = float(current_avg_elem.text)
                except ValueError:
                    dbg.warning("⚠️ Invalid value for current_avg in XML. Using default value.")
            
            return {"total_time": total_time, "count": count, "current_avg": current_avg}
        except (ET.ParseError, IOError, AttributeError, ValueError) as e:
            dbg.warning(f"⚠️ Failed to load stats ({e}). Initializing new stats.")
    return {"total_time": 0.0, "count": 0, "current_avg": 0.0}


def save_global_stats(stats):
    """Save stats to an XML file with proper formatting."""
    root = ET.Element("global_stats")
    ET.SubElement(root, "total_time").text = f"{stats['total_time']:.4f}"
    ET.SubElement(root, "count").text = str(stats["count"])
    ET.SubElement(root, "current_avg").text = f"{stats['current_avg'] * 1000:.4f}"

    # Convert the ElementTree to a string
    xml_string = ET.tostring(root, encoding="utf-8")
    
    # Use minidom to format the XML
    pretty_xml = minidom.parseString(xml_string).toprettyxml(indent="  ")

    try:
        # Write the prettified XML to the file
        with open(STATS_FILE, "w") as file:
            file.write(pretty_xml)
    except IOError as e:
        dbg.error(f"⚠️ Failed to save stats ({e}).")


global_stats = load_global_stats()

def measure_time(func):
    def wrapper(*args, **kwargs):
        # Record start time
        start_time = time.time()

        # Execute the wrapped function
        result = func(*args, **kwargs)

        # Record end time and calculate execution time
        end_time = time.time()
        execution_time_sec = end_time - start_time
        execution_time_ms = execution_time_sec * 1000

        # Update global stats
        global_stats["total_time"] += execution_time_sec
        global_stats["count"] += 1
        global_stats["current_avg"] = (
            global_stats["total_time"] / global_stats["count"]
        )
        save_global_stats(global_stats)

        # Retrieve and log global average time
        avg_time_sec = global_stats["current_avg"]
        avg_time_ms = avg_time_sec * 1000

        if execution_time_sec > 3:
            dbg.warning(
                f"⚠️ Function '{func.__name__}' executed in {execution_time_sec:.2f} seconds "
                f"({execution_time_ms:.2f} ms), exceeding the 3-second threshold! "
                f"(Global Avg: {avg_time_sec:.2f} seconds / {avg_time_ms:.2f} ms)"
            )
        else:
            dbg.info(
                f"Function '{func.__name__}' executed in {execution_time_sec:.2f} seconds "
                f"({execution_time_ms:.2f} ms). "
                f"(Global Avg: {avg_time_sec:.2f} seconds / {avg_time_ms:.2f} ms)"
            )

        return result

    return wrapper
