#!/usr/bin/env python3
"""
Monitoring script for WebSearchTool usage and performance
"""

import os
import sys
import json
import logging
from datetime import datetime
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Add the src directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from greenwashing_detector.tools.web_search import WebSearchTool

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class WebSearchMonitor:
    """Monitor and analyze WebSearchTool usage and performance."""
    
    def __init__(self):
        self.stats = {
            'total_queries': 0,
            'successful_queries': 0,
            'failed_queries': 0,
            'timeout_errors': 0,
            'network_errors': 0,
            'api_errors': 0,
            'esg_topics': {
                'sustainability': 0,
                'carbon_neutral': 0,
                'esg_reporting': 0,
                'greenwashing': 0,
                'certification': 0,
                'compliance': 0
            },
            'query_history': [],
            'performance_metrics': {
                'avg_response_time': 0,
                'total_response_time': 0
            }
        }
        self.web_search = None
        
    def initialize_tool(self):
        """Initialize the WebSearchTool."""
        try:
            self.web_search = WebSearchTool()
            logger.info("✅ WebSearchTool initialized for monitoring")
            return True
        except Exception as e:
            logger.error(f"❌ Failed to initialize WebSearchTool: {str(e)}")
            return False
    
    def test_query(self, query: str) -> dict:
        """Execute a test query and collect metrics."""
        import time
        
        start_time = time.time()
        result = None
        error_type = None
        
        try:
            result = self.web_search._run(query)
            response_time = time.time() - start_time
            
            # Determine if query was successful
            if "error" in result.lower() or "timeout" in result.lower():
                success = False
                if "timeout" in result.lower():
                    error_type = "timeout"
                    self.stats['timeout_errors'] += 1
                elif "network" in result.lower():
                    error_type = "network"
                    self.stats['network_errors'] += 1
                else:
                    error_type = "api"
                    self.stats['api_errors'] += 1
                self.stats['failed_queries'] += 1
            else:
                success = True
                self.stats['successful_queries'] += 1
                self.stats['performance_metrics']['total_response_time'] += response_time
            
            # Update statistics
            self.stats['total_queries'] += 1
            
            # Track query history
            query_record = {
                'timestamp': datetime.now().isoformat(),
                'query': query,
                'success': success,
                'response_time': response_time,
                'error_type': error_type,
                'result_length': len(result) if result else 0
            }
            self.stats['query_history'].append(query_record)
            
            # Categorize ESG topics
            query_lower = query.lower()
            if 'sustainability' in query_lower:
                self.stats['esg_topics']['sustainability'] += 1
            if 'carbon' in query_lower or 'neutral' in query_lower:
                self.stats['esg_topics']['carbon_neutral'] += 1
            if 'esg' in query_lower or 'reporting' in query_lower:
                self.stats['esg_topics']['esg_reporting'] += 1
            if 'greenwashing' in query_lower:
                self.stats['esg_topics']['greenwashing'] += 1
            if 'certification' in query_lower or 'certified' in query_lower:
                self.stats['esg_topics']['certification'] += 1
            if 'compliance' in query_lower:
                self.stats['esg_topics']['compliance'] += 1
            
            return {
                'success': success,
                'response_time': response_time,
                'result': result,
                'error_type': error_type
            }
            
        except Exception as e:
            response_time = time.time() - start_time
            logger.error(f"❌ Exception during query '{query}': {str(e)}")
            self.stats['failed_queries'] += 1
            self.stats['api_errors'] += 1
            self.stats['total_queries'] += 1
            
            query_record = {
                'timestamp': datetime.now().isoformat(),
                'query': query,
                'success': False,
                'response_time': response_time,
                'error_type': 'exception',
                'result_length': 0
            }
            self.stats['query_history'].append(query_record)
            
            return {
                'success': False,
                'response_time': response_time,
                'result': f"Exception: {str(e)}",
                'error_type': 'exception'
            }
    
    def run_test_suite(self):
        """Run a comprehensive test suite."""
        test_queries = [
            "Tesla sustainability claims 2024",
            "ESG greenwashing examples companies",
            "GRI sustainability reporting standards",
            "carbon neutral certification verification",
            "sustainability compliance requirements",
            "ESG reporting best practices",
            "greenwashing detection methods",
            "sustainability certification standards"
        ]
        
        logger.info("🚀 Starting comprehensive test suite...")
        
        for i, query in enumerate(test_queries, 1):
            logger.info(f"\n🔍 Test {i}/{len(test_queries)}: '{query}'")
            result = self.test_query(query)
            
            if result['success']:
                logger.info(f"✅ Success ({result['response_time']:.2f}s)")
            else:
                logger.error(f"❌ Failed ({result['response_time']:.2f}s) - {result['error_type']}")
        
        logger.info("\n📊 Test suite completed!")
    
    def calculate_metrics(self):
        """Calculate performance metrics."""
        if self.stats['successful_queries'] > 0:
            self.stats['performance_metrics']['avg_response_time'] = (
                self.stats['performance_metrics']['total_response_time'] / 
                self.stats['successful_queries']
            )
        
        success_rate = (
            self.stats['successful_queries'] / self.stats['total_queries'] * 100
        ) if self.stats['total_queries'] > 0 else 0
        
        return {
            'success_rate': success_rate,
            'total_queries': self.stats['total_queries'],
            'successful_queries': self.stats['successful_queries'],
            'failed_queries': self.stats['failed_queries'],
            'avg_response_time': self.stats['performance_metrics']['avg_response_time'],
            'error_breakdown': {
                'timeout_errors': self.stats['timeout_errors'],
                'network_errors': self.stats['network_errors'],
                'api_errors': self.stats['api_errors']
            }
        }
    
    def generate_report(self):
        """Generate a comprehensive monitoring report."""
        metrics = self.calculate_metrics()
        
        report = {
            'timestamp': datetime.now().isoformat(),
            'summary': {
                'total_queries': metrics['total_queries'],
                'success_rate': f"{metrics['success_rate']:.1f}%",
                'avg_response_time': f"{metrics['avg_response_time']:.2f}s",
                'error_breakdown': metrics['error_breakdown']
            },
            'esg_topic_coverage': self.stats['esg_topics'],
            'recent_queries': self.stats['query_history'][-10:],  # Last 10 queries
            'recommendations': self._generate_recommendations(metrics)
        }
        
        return report
    
    def _generate_recommendations(self, metrics):
        """Generate recommendations based on metrics."""
        recommendations = []
        
        if metrics['success_rate'] < 80:
            recommendations.append({
                'type': 'warning',
                'message': 'Low success rate detected. Check network connectivity and API key validity.',
                'priority': 'high'
            })
        
        if metrics['avg_response_time'] > 10:
            recommendations.append({
                'type': 'performance',
                'message': 'High average response time. Consider optimizing queries or checking API performance.',
                'priority': 'medium'
            })
        
        if metrics['error_breakdown']['timeout_errors'] > 0:
            recommendations.append({
                'type': 'timeout',
                'message': 'Timeout errors detected. Consider increasing timeout values or checking network stability.',
                'priority': 'medium'
            })
        
        if not recommendations:
            recommendations.append({
                'type': 'success',
                'message': 'All metrics look good! WebSearchTool is performing well.',
                'priority': 'low'
            })
        
        return recommendations
    
    def save_report(self, filename: str = None):
        """Save the monitoring report to a file."""
        if filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"web_search_monitoring_report_{timestamp}.json"
        
        report = self.generate_report()
        
        with open(filename, 'w') as f:
            json.dump(report, f, indent=2)
        
        logger.info(f"📄 Report saved to: {filename}")
        return filename

def main():
    """Main monitoring function."""
    print("🔍 WebSearchTool Monitoring and Analysis")
    print("=" * 50)
    
    # Initialize monitor
    monitor = WebSearchMonitor()
    
    # Initialize tool
    if not monitor.initialize_tool():
        print("❌ Failed to initialize WebSearchTool. Exiting.")
        return
    
    # Run test suite
    monitor.run_test_suite()
    
    # Generate and display report
    report = monitor.generate_report()
    
    print("\n📊 MONITORING REPORT")
    print("=" * 50)
    print(f"📅 Timestamp: {report['timestamp']}")
    print(f"🔢 Total Queries: {report['summary']['total_queries']}")
    print(f"✅ Success Rate: {report['summary']['success_rate']}")
    print(f"⏱️  Avg Response Time: {report['summary']['avg_response_time']}")
    
    print("\n🚨 Error Breakdown:")
    for error_type, count in report['summary']['error_breakdown'].items():
        print(f"   {error_type}: {count}")
    
    print("\n📈 ESG Topic Coverage:")
    for topic, count in report['esg_topic_coverage'].items():
        print(f"   {topic}: {count}")
    
    print("\n💡 Recommendations:")
    for rec in report['recommendations']:
        print(f"   [{rec['priority'].upper()}] {rec['message']}")
    
    # Save report
    filename = monitor.save_report()
    print(f"\n📄 Detailed report saved to: {filename}")

if __name__ == "__main__":
    main() 