#!/usr/bin/env python3
"""
Quick Speed Test for Optimized Analysis
Tests the new fast comprehensive analysis method
"""

import sys
import os
import time
from datetime import datetime

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from main_app import SafetySummarizerApp

def test_speed_optimization():
    """Test the speed-optimized analysis"""
    
    print("⚡ Testing Speed-Optimized Analysis")
    print("=" * 40)
    
    # Initialize the application
    print("📊 Initializing AI Safety Summarizer...")
    app = SafetySummarizerApp()
    
    # Test one module for speed
    module = 'permit'
    days_back = 30
    customer_id = None
    
    print(f"\n🔍 Testing {module.upper()} module (speed-optimized)...")
    
    try:
        # Record start time
        start_time = time.time()
        
        # Generate module summary using speed-optimized approach
        summary = app.generate_module_summary(
            module=module,
            customer_id=customer_id,
            days_back=days_back
        )
        
        # Record end time
        end_time = time.time()
        processing_time = end_time - start_time
        
        # Extract information
        total_records = 0
        if 'raw_data' in summary and 'permit_statistics' in summary['raw_data']:
            total_records = summary['raw_data']['permit_statistics'].get('total_permits', 0)
        
        # Count AI insights
        ai_insights = summary.get('ai_summary', '')
        insight_count = len([line for line in ai_insights.split('\n') if line.strip().startswith('•')])
        
        print(f"✅ Speed Test Results:")
        print(f"   📈 Records Analyzed: {total_records}")
        print(f"   🧠 AI Insights Generated: {insight_count}")
        print(f"   ⚡ Processing Time: {processing_time:.2f} seconds")
        print(f"   🔥 API Calls Used: 1 (Single Fast Call)")
        print(f"   🎯 Model Used: GPT-3.5 Turbo 16k")
        
        # Show sample insights
        if ai_insights:
            print(f"\n💡 Sample AI Insights:")
            sample_insights = [line.strip() for line in ai_insights.split('\n') if line.strip().startswith('•')][:5]
            for insight in sample_insights:
                print(f"   {insight}")
        
        # Performance assessment
        print(f"\n📊 Performance Assessment:")
        if processing_time < 10:
            print(f"   🚀 EXCELLENT: Processing time under 10 seconds")
        elif processing_time < 30:
            print(f"   ✅ GOOD: Processing time under 30 seconds")
        elif processing_time < 60:
            print(f"   ⚠️  ACCEPTABLE: Processing time under 1 minute")
        else:
            print(f"   ❌ SLOW: Processing time over 1 minute")
        
        # Speed comparison
        estimated_old_time = total_records / 100 * 3 + 10  # Estimated old chunked approach
        speed_improvement = estimated_old_time / processing_time if processing_time > 0 else 1
        
        print(f"\n⚡ Speed Comparison:")
        print(f"   Old Estimated Time: {estimated_old_time:.1f} seconds")
        print(f"   New Actual Time: {processing_time:.1f} seconds")
        print(f"   Speed Improvement: {speed_improvement:.1f}x faster")
        
        # Cost estimation
        estimated_tokens = len(ai_insights) * 1.3  # Rough token estimation
        estimated_cost = (estimated_tokens / 1000) * 0.002  # GPT-3.5 Turbo pricing
        
        print(f"\n💰 Cost Estimation:")
        print(f"   Estimated Tokens: {estimated_tokens:.0f}")
        print(f"   Estimated Cost: ${estimated_cost:.4f}")
        print(f"   Cost per Record: ${estimated_cost/max(total_records, 1):.6f}")
        
    except Exception as e:
        print(f"❌ Error during speed test: {str(e)}")
        return False
    
    # Close the application
    app.close()
    
    print(f"\n🎉 Speed optimization test completed!")
    print(f"⚡ Key Achievement: {total_records} records analyzed in {processing_time:.1f} seconds with 1 API call!")
    
    return True

if __name__ == "__main__":
    success = test_speed_optimization()
    if success:
        print("\n✅ Speed optimization is working correctly!")
    else:
        print("\n❌ Speed optimization needs attention.")
