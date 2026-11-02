import os
import requests
from mcp.server.fastmcp import FastMCP

# Initialize the MCP server using FastMCP
mcp = FastMCP("GSA DAP Analytics Explorer")
API_BASE_URL = "https://api.gsa.gov/analytics/dap/v2"

def get_api_key():
    api_key = os.getenv("ANALYTICS_API_KEY")
    if not api_key:
        raise ValueError("ANALYTICS_API_KEY environment variable is not set.")
    return api_key

@mcp.tool()
def get_dap_analytics(report: str, agency: str = None, domain: str = None) -> str:
    """Fetches historical or real-time analytics data from the GSA Digital Analytics Program (DAP) API v2.
    
    Parameters:
    - report: One of 'domain', 'download', 'second-level-domain', or 'top-pages-realtime'
    - agency: Optional uppercase acronym (e.g. 'HHS', 'USDA', 'GSA')
    - domain: Optional specific subdomain or domain to filter by (e.g., 'nlm.nih.gov')
    """
    api_key = get_api_key()
    clean_domain = domain.strip().lower() if domain else ""

    if clean_domain and report != 'top-pages-realtime':
        endpoint = f"{API_BASE_URL}/domain/{clean_domain}/reports/{report}/data"
    else:
        endpoint = f"{API_BASE_URL}/reports/{report}/data"

    params = {}
    if agency and agency.lower() != 'all' and not clean_domain:
        if report not in ['top-pages-realtime', 'second-level-domain']:
            params['agency'] = agency

    headers = {"X-API-KEY": api_key}

    try:
        response = requests.get(endpoint, headers=headers, params=params)
        if response.status_code != 200:
            return f"API Error {response.status_code}: {response.text}"

        data = response.json()
        if not data:
            return "No records found for the given criteria."

        if clean_domain and report == 'top-pages-realtime':
            filtered_data = []
            for row in data:
                domain_val = str(row.get('domain', '')).lower()
                page_val = str(row.get('page', '')).lower()
                if clean_domain in domain_val or clean_domain in page_val:
                    filtered_data.append(row)
            data = filtered_data

        if not data:
            return f"No matching records found for domain '{clean_domain}' in the realtime dataset."

        return str(data[:15])

    except Exception as e:
        return f"An unexpected exception occurred: {str(e)}"

if __name__ == "__main__":
    mcp.run()
