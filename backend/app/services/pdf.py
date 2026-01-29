from weasyprint import HTML, CSS
from jinja2 import Environment
import os
from datetime import datetime
import pytz

def generate_pdf(data: dict, output_path: str = "output.pdf"):
    """
    Generates a high-quality PDF report using the rich data provided.
    Implements timezone conversion and horizontal weather layout.
    """
    
    # helper for timezone conversion
    def format_time(iso_str, tz_name, fmt="%H:%M"):
        if not iso_str: return "-"
        try:
            dt = datetime.fromisoformat(iso_str)
            if tz_name and tz_name != "UTC":
                target_tz = pytz.timezone(tz_name)
                dt = dt.astimezone(target_tz)
            return dt.strftime(fmt)
        except:
            return iso_str

    # helper for weather icon
    def get_weather_icon(cloud_cover):
        base_path = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        img_dir = os.path.join(base_path, "data", "img", "cloudcover")
        
        filename = "cloudy.svg"
        if cloud_cover < 10: filename = "clear.svg"
        elif cloud_cover < 30: filename = "mostlyclear.svg"
        elif cloud_cover < 70: filename = "partlycloudy.svg"
        
        full_path = os.path.join(img_dir, filename)
        if os.path.exists(full_path):
            return "file://" + full_path
        return "" 

    # Helper for planet images
    def get_planet_image(planet_name):
        base_path = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        img_dir = os.path.join(base_path, "data", "img", "planets")
        
        # Normalize name
        name_lower = planet_name.lower()
        
        # Try extensions
        for ext in [".png", ".jpg", ".jpeg"]:
            full_path = os.path.join(img_dir, name_lower + ext)
            if os.path.exists(full_path):
                return "file://" + full_path
        
        return "" # Return empty if not found, CSS will handle fallback or empty

    env = Environment()
    env.filters['fmt_time'] = format_time
    env.globals['get_weather_icon'] = get_weather_icon
    env.globals['get_planet_image'] = get_planet_image
    
    # Moon Image from Data (NASA API)

    
    html_template = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Observation Plan</title>
        <style>
            @page {
                size: A4;
                margin: 1.5cm;
                @bottom-center {
                    content: "AstroBuddy Report | Page " counter(page);
                    font-size: 9px; color: #888;
                }
            }
            /* Global Reset & Typography */
            body { 
                font-family: 'Helvetica Neue', Helvetica, Arial, sans-serif; 
                color: #000; 
                font-size: 10pt; 
                line-height: 1.4; 
            }
            h1 { 
                font-size: 24pt; 
                font-weight: 700;
                margin: 0 0 10px 0; 
                color: #000; 
                text-transform: uppercase;
                letter-spacing: 1px;
            }
            
            /* Header Metadata */
            .header-meta {
                margin-bottom: 30px;
                font-size: 10pt;
                color: #000;
                line-height: 1.5;
            }
            .meta-line {
                display: block;
            }
            .meta-label {
                font-weight: bold;
                margin-right: 5px;
                text-transform: uppercase;
                font-size: 0.8em;
                color: #555;
            }

            /* Section Headers */
            h2 { 
                font-size: 14pt; 
                border-bottom: 1px solid #000; 
                padding-bottom: 5px; 
                margin-top: 30px; 
                margin-bottom: 15px; 
                color: #000; 
                text-transform: uppercase;
                letter-spacing: 0.5px;
                font-weight: 600;
            }
            
            /* Overview */
            .overview { 
                background: #f4f4f4; 
                border-left: 3px solid #000; 
                padding: 15px; 
                font-style: italic; 
                color: #333; 
                border-radius: 0; 
            }
            
            /* Horizontal Weather */
            .weather-scroll { 
                display: flex; 
                gap: 0; 
                border: 1px solid #000; 
                border-radius: 0; 
                overflow: hidden; 
                margin-top: 10px; 
            }
            .weather-card { 
                flex: 1; 
                text-align: center; 
                padding: 10px 5px; 
                border-right: 1px solid #000; 
                min-width: 50px;
                display: flex;
                flex-direction: column;
                align-items: center;
                justify-content: center; 
            }
            .weather-card:last-child { border-right: none; }
            .w-time { font-weight: bold; font-size: 0.9em; color: #000; margin-bottom: 5px; }
            
            .w-icon { 
                width: 44px; 
                height: 44px; 
                margin: 5px 0;
                display: flex;
                align-items: center;
                justify-content: center;
            }
            .w-icon img {
                width: 100%;
                height: 100%;
                object-fit: contain;
            }
            
            .w-temp { font-weight: bold; color: #000; }
            .w-clouds { font-size: 0.8em; color: #666; }
            
            /* Moon & Sun */
            .astro-grid { display: flex; gap: 20px; margin-top: 15px; }
            .astro-card { 
                flex: 1; 
                background: #000; 
                color: white; 
                padding: 15px; 
                border-radius: 0; 
                display: flex; 
                align-items: center; 
                gap: 15px; 
            }
            
            .moon-visual { 
                width: 80px; 
                height: 80px; 
                background: #111; 
                border-radius: 50%; /* Moon acts as natural circle, nice contrast to square theme */
                overflow: hidden; 
                display:flex; 
                align-items:center; 
                justify-content:center; 
                color: #fff; 
                font-size:0.7em;
                border: 1px solid #333;
            } 
            .moon-visual img { width: 100%; height: 100%; object-fit: cover; } 
            
            .astro-info div { margin-bottom: 2px; font-size: 0.9em; }
            .astro-label { color: #aaa; font-size: 0.8em; text-transform: uppercase; letter-spacing: 1px; }
            
            .sun-times { 
                display: flex; 
                justify-content: space-between; 
                font-size: 0.9em; 
                color: #ccc; 
                margin-top: 10px; 
                border-top: 1px solid #333; 
                padding-top: 10px; 
            }

            /* Planets Cards */
            .planet-grid { display: flex; flex-wrap: wrap; gap: 15px; margin-top: 10px; }
            .planet-card { 
                width: 47%; 
                background: white;
                border: 1px solid #000;
                border-radius: 0;
                display: flex;
                overflow: hidden;
                page-break-inside: avoid;
                min-height: 80px; 
            }
            .planet-img-box {
                width: 80px;
                background-color: #000;
                display: flex;
                align-items: center;
                justify-content: center;
                flex-shrink: 0;
            }
            .planet-img-box img {
                max-width: 100%;
                max-height: 100%;
                object-fit: contain;
            }
            .planet-data {
                padding: 10px;
                flex: 1;
                display: flex;
                flex-direction: column;
                justify-content: center;
            }
            .planet-name {
                font-size: 1.1em;
                font-weight: bold;
                color: #000;
                margin-bottom: 5px;
                border-bottom: 1px solid #eee;
                padding-bottom: 2px;
                text-transform: uppercase;
            }
            .planet-metrics {
                font-size: 0.85em;
                color: #333;
                display: grid;
                grid-template-columns: 1fr 1fr;
                gap: 2px 10px;
            }
            .metric-label { color: #666; font-size: 0.9em; margin-right: 4px; }


            /* DSO Cards */
            .dso-card { 
                border: 1px solid #000; 
                border-radius: 0; 
                margin-bottom: 20px; 
                page-break-inside: avoid; 
            }
            .dso-header { 
                background: #000; 
                color: white; 
                padding: 12px 15px; 
                border-radius: 0; 
                display: flex; 
                justify-content: space-between; 
                align-items: baseline; 
            }
            .dso-name { font-size: 1.2em; font-weight: bold; text-transform: uppercase; }
            .dso-meta { font-size: 0.9em; opacity: 0.8; }
            .dso-body { padding: 15px; }
            
            .dso-stats { 
                display: flex; 
                background: #f4f4f4; 
                padding: 10px; 
                border: 1px solid #e0e0e0;
                border-radius: 0; 
                margin-bottom: 15px; 
                justify-content: space-around; 
                font-size: 0.9em; 
            }
            .stat-item strong { display: block; color: #555; font-size: 0.8em; text-transform: uppercase; }
            
            .dso-desc { text-align: justify; margin-bottom: 15px; color: #000; }
            
            .dso-extras { display: flex; gap: 15px; }
            .extra-box { flex: 1; padding: 10px; border-radius: 0; font-size: 0.9em; border: 1px solid #eee; }
            .tip-box { background: #fafafa; border-left: 3px solid #000; color: #333; }
            .fact-box { background: #fafafa; border-left: 3px solid #666; color: #333; }

        </style>
    </head>
    <body>
        <div>
            <h1>Observation Report</h1>
            <div class="header-meta">
                <div class="meta-line">
                    <span class="meta-label">Date:</span> {{ date }}
                </div>
                <div class="meta-line">
                    <span class="meta-label">Location:</span> {{ location.lat }}, {{ location.lon }}
                </div>
                <div class="meta-line">
                    <span class="meta-label">Telescope:</span> {{ telescope if telescope else 'Not specified' }}
                </div>
                <div class="meta-line">
                    <span class="meta-label">Timezone:</span> {{ timezone }}
                </div>
            </div>
        </div>

        <div class="overview">
            <span style="font-size:1.0em; font-weight:bold; text-transform:uppercase;">Night Overview:</span> {{ ai.overview }}
        </div>

        <!-- CONDITIONS -->
        <h2>Conditions</h2>
        <div class="astro-grid">
            <!-- Darkness / Sun -->
            <div class="astro-card">
                <div class="astro-info" style="width:100%">
                    <div class="astro-label">Darkness Window</div>
                    <div style="font-size: 1.4em; font-weight:bold; color: #fff;">
                        {% if astro.darkness_window.start and astro.darkness_window.end %}
                            {{ astro.darkness_window.start | fmt_time(timezone) }} - {{ astro.darkness_window.end | fmt_time(timezone) }}
                        {% else %}
                            No Astronomical Darkness
                        {% endif %}
                    </div>
                    <div class="sun-times">
                        <span>Sunset: {{ astro.sun.set | fmt_time(timezone) }}</span>
                        <span>Sunrise: {{ astro.sun.rise | fmt_time(timezone) }}</span>
                    </div>
                </div>
            </div>
            
            <!-- Moon -->
            <div class="astro-card">
                <div class="moon-visual">
                    {% if astro.moon.image_url %}
                        <img src="{{ astro.moon.image_url }}" alt="Moon Phase">
                    {% else %}
                        Moon
                    {% endif %}
                </div>
                <div class="astro-info">
                    <div class="astro-label">{{ astro.moon.phase_name }}</div>
                    <div style="font-size: 1.2em; font-weight:bold;">{{ astro.moon.illumination }}% Illumination</div>
                    <div>Rise: {{ astro.moon.rise | fmt_time(timezone) }} | Set: {{ astro.moon.set | fmt_time(timezone) }}</div>
                </div>
            </div>
        </div>

        <!-- Weather Strip -->
        <h2 style="font-size: 10pt; margin-top:20px; border-bottom:none; margin-bottom: 5px; color:#555;">Hourly Forecast</h2>
        <div class="weather-scroll">
            {% for hour in weather.hourly %}
            <div class="weather-card">
                <div class="w-time">{{ hour.ts | fmt_time(timezone, "%H") }}h</div>
                <div class="w-icon">
                    <img src="{{ get_weather_icon(hour.clouds) }}" alt="Weather Icon" />
                </div>
                <div class="w-temp">{{ hour.temp }}°</div>
                <div class="w-clouds">{{ hour.clouds }}%</div>
            </div>
            {% endfor %}
        </div>

        <!-- PLANETS -->
        <h2>Solar System</h2>
        <p style="font-size:0.9em; color:#666; margin-top:-10px;">Planets visible during darkness.</p>
        
        <div class="planet-grid">
            {% for planet in planets %}
                {% if planet.is_visible %}
                <div class="planet-card">
                    <div class="planet-img-box">
                        <img src="{{ get_planet_image(planet.name) }}" alt="{{ planet.name }}">
                    </div>
                    <div class="planet-data">
                        <div class="planet-name">{{ planet.name }}</div>
                        <div class="planet-metrics">
                            <div class="metric-row"><span class="metric-label">Mag:</span> {{ planet.magnitude }}</div>
                            <div class="metric-row"><span class="metric-label">Dist:</span> {{ planet.distance_au }} AU</div>
                            <div class="metric-row"><span class="metric-label">Rise:</span> {{ planet.rise | fmt_time(timezone) }}</div>
                            <div class="metric-row"><span class="metric-label">Set:</span> {{ planet.set | fmt_time(timezone) }}</div>
                        </div>
                    </div>
                </div>
                {% endif %}
            {% endfor %}
        </div>

        <!-- DEEP SKY OBJECTS -->
        <h2>Deep Sky Objects</h2>
        {% for obj in ai.objects %}
        <div class="dso-card">
            <div class="dso-header">
                <div class="dso-name">#{{ obj.ranking }} {{ obj.id }} {% if obj.common_name %}({{ obj.common_name }}){% endif %}</div>
                <div class="dso-meta">{{ obj.type }} &bull; {{ obj.constellation }}</div>
            </div>
            <div class="dso-body">
                <div class="dso-stats">
                    <div class="stat-item"><strong>Mag</strong> {{ obj.mag if obj.mag else 'N/A' }}</div>
                    <div class="stat-item"><strong>Size</strong> {{ obj.size }}</div>
                    <div class="stat-item"><strong>Rise</strong> {{ obj.rise | fmt_time(timezone) }}</div>
                    <div class="stat-item"><strong>Transit</strong> {{ obj.transit | fmt_time(timezone) }} ({{ obj.transit_altitude }}°)</div>
                    <div class="stat-item"><strong>Set</strong> {{ obj.set | fmt_time(timezone) }}</div>
                </div>
                
                <div class="dso-desc">
                    {{ obj.description }}
                </div>
                
                <div class="dso-extras">
                    <div class="extra-box tip-box">
                        <strong>Tips:</strong> {{ obj.tips }}
                    </div>
                    <div class="extra-box fact-box">
                        <strong>Fact:</strong> {{ obj.fact }}
                    </div>
                </div>
            </div>
        </div>
        {% endfor %}

        <!-- OTHER VISIBLE OBJECTS (NON-FEATURED) -->
        {% if non_featured_objects and non_featured_objects|length > 0 %}
        <h2 style="margin-top: 30px;">Other Visible Objects</h2>
        <p style="font-size:0.9em; color:#666; margin-top:-10px; margin-bottom: 15px;">
            Additional {{ non_featured_objects|length }} objects visible tonight, ordered by magnitude.
        </p>
        
        <table style="width: 100%; border-collapse: collapse; font-size: 0.85em; margin-top: 10px;">
            <thead>
                <tr style="background: #f4f4f4; border-bottom: 2px solid #000;">
                    <th style="padding: 8px; text-align: left; font-weight: bold; text-transform: uppercase; font-size: 0.8em;">ID</th>
                    <th style="padding: 8px; text-align: left; font-weight: bold; text-transform: uppercase; font-size: 0.8em;">Name</th>
                    <th style="padding: 8px; text-align: left; font-weight: bold; text-transform: uppercase; font-size: 0.8em;">Type</th>
                    <th style="padding: 8px; text-align: left; font-weight: bold; text-transform: uppercase; font-size: 0.8em;">Constellation</th>
                    <th style="padding: 8px; text-align: center; font-weight: bold; text-transform: uppercase; font-size: 0.8em;">Mag</th>
                    <th style="padding: 8px; text-align: left; font-weight: bold; text-transform: uppercase; font-size: 0.8em;">Size</th>
                </tr>
            </thead>
            <tbody>
                {% for obj in non_featured_objects %}
                <tr style="border-bottom: 1px solid #e0e0e0; {% if loop.index % 2 == 0 %}background: #fafafa;{% endif %}">
                    <td style="padding: 6px 8px; font-weight: bold;">{{ obj.id }}</td>
                    <td style="padding: 6px 8px;">{{ obj.name if obj.name else '—' }}</td>
                    <td style="padding: 6px 8px;">{{ obj.type if obj.type else '—' }}</td>
                    <td style="padding: 6px 8px;">{{ obj.constellation if obj.constellation else '—' }}</td>
                    <td style="padding: 6px 8px; text-align: center; font-family: monospace;">{{ obj.mag if obj.mag else '—' }}</td>
                    <td style="padding: 6px 8px;">{{ obj.size if obj.size else '—' }}</td>
                </tr>
                {% endfor %}
            </tbody>
        </table>
        {% endif %}

    </body>
    </html>
    """
    
    template = env.from_string(html_template)
    rendered_html = template.render(**data)
    
    HTML(string=rendered_html).write_pdf(output_path)
    return output_path
