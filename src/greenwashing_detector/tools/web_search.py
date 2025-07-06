from typing import Any, Annotated
from crewai.tools import BaseTool
import requests
import os
import logging
from dotenv import load_dotenv
from pydantic import Field

# Load environment variables
load_dotenv()

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class WebSearchTool(BaseTool):
    """Tool for performing web searches using Serper API (via GET)."""
    
    name: Annotated[str, "WebSearchTool"] = "WebSearchTool"
    description: Annotated[str, "Tool description"] = """
    Use this tool to search the web for information about companies, ESG claims, 
    sustainability standards, and industry benchmarks. The tool returns relevant 
    search results that can help validate or fact-check ESG-related claims.
    """
    
    api_key: Annotated[str, "API key"] = Field(default="")
    base_url: Annotated[str, "Base URL"] = Field(default="https://google.serper.dev/search")
    
    def model_post_init(self, __context: Any) -> None:
        """Initialize the tool with API key from environment."""
        self.api_key = os.getenv('SERPER_API_KEY', '')
        if not self.api_key:
            logger.warning("⚠️ SERPER_API_KEY not found in environment variables")
        else:
            logger.info("✅ WebSearchTool initialized with Serper API")
            logger.info(f"🔑 API Key: {self.api_key[:8]}...{self.api_key[-4:]}")
    
    def _run(self, query: str) -> str:
        """
        Execute a web search using Serper API (GET).
        
        Args:
            query: The search query to execute
            
        Returns:
            Formatted search results as a string
        """
        if not self.api_key:
            return "❌ Error: SERPER_API_KEY not configured"
        
        logger.info(f"🔍 WebSearchTool executing query: '{query}'")

        headers = {
            'X-API-KEY': self.api_key,
            'User-Agent': 'Mozilla/5.0'
        }
        
        params = {
            'q': query,
            'gl': 'us',
            'hl': 'en'
        }

        try:
            response = requests.get(self.base_url, headers=headers, params=params, timeout=15)
            logger.info(f"📊 Response status: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                logger.info("✅ Search completed successfully")
                return self._format_results(data, query)
            else:
                logger.error(f"❌ API returned status {response.status_code}: {response.text}")
                return f"❌ API Error: {response.status_code} - {response.text}"
                
        except requests.exceptions.RequestException as e:
            logger.error(f"🌐 Network error: {e}")
            return f"❌ Network error: {e}"
    
    def _format_results(self, data: dict, query: str) -> str:
        """Format the search results into a readable string."""
        try:
            results = []
            results.append(f"🔍 Search Results for: '{query}'")
            results.append("=" * 50)
            
            # Add organic results
            if 'organic' in data and data['organic']:
                results.append("📄 Organic Results:")
                for i, result in enumerate(data['organic'][:3], 1):
                    title = result.get('title', 'No title')
                    snippet = result.get('snippet', 'No description')
                    link = result.get('link', 'No link')
                    results.append(f"{i}. {title}")
                    results.append(f"   📝 {snippet}")
                    results.append(f"   🔗 {link}")
                    results.append("")
            
            # Add knowledge graph if available
            if 'knowledgeGraph' in data and data['knowledgeGraph']:
                kg = data['knowledgeGraph']
                results.append("🧠 Knowledge Graph:")
                results.append(f"   📋 {kg.get('title', 'No title')}")
                results.append(f"   📝 {kg.get('description', 'No description')}")
                results.append("")
            
            # Add answer box if available
            if 'answerBox' in data and data['answerBox']:
                answer = data['answerBox']
                results.append("💡 Answer Box:")
                results.append(f"   📋 {answer.get('title', 'No title')}")
                results.append(f"   📝 {answer.get('snippet', 'No answer')}")
                results.append("")
            
            if len(results) <= 2:  # Only header and separator
                results.append("❌ No results found")
            
            return "\n".join(results)
            
        except Exception as e:
            logger.error(f"❌ Error formatting results: {e}")
            return f"❌ Error processing search results: {e}"

    def _run_async(self, *args: Any, **kwargs: Any) -> Any:
        """Async implementation - defaults to sync version."""
        return self._run(*args, **kwargs)
