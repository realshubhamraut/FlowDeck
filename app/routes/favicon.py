"""
Favicon generation routes
Generates dynamic SVG favicons based on page context
"""
from flask import Blueprint, Response, request

bp = Blueprint('favicon', __name__)

# Color schemes for different sections
FAVICON_COLORS = {
    'dashboard': '#0d6efd',  # Bootstrap primary blue
    'tasks': '#198754',      # Bootstrap success green
    'chat': '#0dcaf0',       # Bootstrap info cyan
    'admin': '#dc3545',      # Bootstrap danger red
    'user': '#6f42c1',       # Bootstrap purple
    'calendar': '#fd7e14',   # Bootstrap orange
    'analytics': '#20c997',  # Bootstrap teal
    'default': '#6c757d'     # Bootstrap secondary gray
}

# Icons for different sections (Font Awesome classes converted to symbols)
FAVICON_ICONS = {
    'dashboard': '■',        # Home/dashboard
    'tasks': '✓',            # Checkmark for tasks
    'chat': '💬',            # Chat bubble
    'admin': '⚙',            # Settings gear
    'user': '👤',            # User profile
    'calendar': '📅',        # Calendar
    'analytics': '📊',       # Chart
    'default': 'F'           # FlowDeck initial
}


def get_section_from_referrer():
    """Determine which section the favicon request is from"""
    referrer = request.referrer or ''
    
    if '/dashboard' in referrer:
        if '/analytics' in referrer:
            return 'analytics'
        if '/calendar' in referrer:
            return 'calendar'
        return 'dashboard'
    elif '/tasks' in referrer:
        return 'tasks'
    elif '/chat' in referrer:
        return 'chat'
    elif '/admin' in referrer:
        return 'admin'
    elif '/user' in referrer or '/profile' in referrer or '/settings' in referrer:
        return 'user'
    else:
        return 'default'


def generate_svg_favicon(section='default'):
    """Generate an SVG favicon for the given section"""
    color = FAVICON_COLORS.get(section, FAVICON_COLORS['default'])
    icon = FAVICON_ICONS.get(section, FAVICON_ICONS['default'])
    
    svg = f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 32 32">
  <defs>
    <linearGradient id="grad" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" style="stop-color:{color};stop-opacity:1" />
      <stop offset="100%" style="stop-color:{color};stop-opacity:0.8" />
    </linearGradient>
  </defs>
  <rect width="32" height="32" rx="6" fill="url(#grad)"/>
  <text x="16" y="22" font-family="Arial, sans-serif" font-size="18" font-weight="bold" 
        fill="white" text-anchor="middle">{icon}</text>
</svg>'''
    
    return svg


@bp.route('/favicon.ico')
def favicon():
    """Serve dynamic favicon based on referrer"""
    section = get_section_from_referrer()
    svg_content = generate_svg_favicon(section)
    
    return Response(svg_content, mimetype='image/svg+xml')


@bp.route('/favicon-<section>.svg')
def favicon_section(section):
    """Serve specific section favicon"""
    if section not in FAVICON_COLORS:
        section = 'default'
    
    svg_content = generate_svg_favicon(section)
    return Response(svg_content, mimetype='image/svg+xml')
