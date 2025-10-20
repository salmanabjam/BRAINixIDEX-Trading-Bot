"""
BiX TradeBOT - Fundamental News Analyzer
========================================
دریافت و تحلیل اخبار فاندامنتال از TradingView برای ارزهای دیجیتال

Author: SALMAN ThinkTank AI Core
Version: 2.0.0
"""

import requests
import json
import logging
from datetime import datetime
from typing import Dict, List, Any, Optional
from pathlib import Path
import time

logger = logging.getLogger(__name__)


class FundamentalNewsAnalyzer:
    """
    دریافت و تحلیل اخبار فاندامنتال از TradingView
    
    Features:
    - دریافت اخبار از چندین منبع TradingView
    - تحلیل سنتیمنت اخبار (مثبت/منفی/خنثی)
    - ذخیره‌سازی ساختاریافته در JSON
    - پشتیبانی از تمام ارزهای دیجیتال Binance
    """

    def __init__(self, symbol: str = "BTCUSDT", exchange: str = "BINANCE"):
        """
        Initialize Fundamental News Analyzer.
        
        Args:
            symbol: نماد ارز دیجیتال (مثال: BTCUSDT, ADAUSDT, SOLUSDT)
            exchange: صرافی (پیش‌فرض: BINANCE)
        """
        self.symbol = symbol
        self.exchange = exchange
        self.base_symbol = symbol.replace("USDT", "").replace("BUSD", "")
        
        # مسیر ذخیره‌سازی
        self.news_dir = Path("news_data")
        self.news_dir.mkdir(exist_ok=True)
        
        # Headers برای درخواست‌ها
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            'Accept': 'application/json',
            'Accept-Language': 'en-US,en;q=0.9',
            'Referer': 'https://www.tradingview.com/'
        }
        
        logger.info(f"📰 Fundamental News Analyzer initialized for {symbol}")

    def _build_tradingview_symbol(self) -> str:
        """ساخت نماد TradingView"""
        return f"{self.exchange}%3A{self.symbol}"

    def fetch_news_headlines(self) -> List[Dict[str, Any]]:
        """
        دریافت سرخط اخبار از TradingView
        
        Returns:
            لیست اخبار با جزئیات کامل
        """
        tv_symbol = self._build_tradingview_symbol()
        
        # دو URL مختلف برای دریافت اخبار
        urls = [
            f"https://news-headlines.tradingview.com/v2/view/headlines/symbol?client=landing&lang=en&section=&streaming=true&symbol={tv_symbol}",
            f"https://news-headlines.tradingview.com/v2/view/headlines/symbol?client=overview&lang=en&symbol={tv_symbol}"
        ]
        
        all_news = []
        
        for url in urls:
            try:
                logger.info(f"📥 Fetching news from: {url[:80]}...")
                response = requests.get(url, headers=self.headers, timeout=10)
                
                if response.status_code == 200:
                    data = response.json()
                    
                    # استخراج اخبار
                    if isinstance(data, dict) and 'items' in data:
                        news_items = data['items']
                    elif isinstance(data, list):
                        news_items = data
                    else:
                        news_items = []
                    
                    for item in news_items:
                        news_entry = self._parse_news_item(item)
                        if news_entry and news_entry not in all_news:
                            all_news.append(news_entry)
                    
                    logger.info(f"✅ Fetched {len(news_items)} news from this source")
                else:
                    logger.warning(f"⚠️ HTTP {response.status_code} for {url[:50]}")
                    
            except Exception as e:
                logger.error(f"❌ Error fetching from {url[:50]}: {e}")
            
            time.sleep(0.5)  # Rate limiting
        
        logger.info(f"📊 Total unique news fetched: {len(all_news)}")
        return all_news

    def fetch_community_ideas(self) -> List[Dict[str, Any]]:
        """
        دریافت ایده‌های تحلیلی کاربران TradingView
        
        Returns:
            لیست ایده‌های تحلیلی
        """
        url = f"https://www.tradingview.com/symbols/{self.symbol}/ideas/?exchange={self.exchange}&component-data-only=1"
        
        try:
            logger.info(f"💡 Fetching community ideas...")
            response = requests.get(url, headers=self.headers, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                ideas = []
                
                # استخراج ایده‌ها (ساختار ممکن است متفاوت باشد)
                if isinstance(data, dict):
                    ideas_list = data.get('ideas', []) or data.get('data', [])
                    
                    for idea in ideas_list:
                        idea_entry = self._parse_idea_item(idea)
                        if idea_entry:
                            ideas.append(idea_entry)
                
                logger.info(f"✅ Fetched {len(ideas)} community ideas")
                return ideas
            else:
                logger.warning(f"⚠️ HTTP {response.status_code} for ideas")
                return []
                
        except Exception as e:
            logger.error(f"❌ Error fetching ideas: {e}")
            return []

    def fetch_conversation_status(self) -> Dict[str, Any]:
        """
        دریافت وضعیت گفتگوها و سنتیمنت کاربران
        
        Returns:
            دیکشنری حاوی تحلیل سنتیمنت
        """
        tv_symbol = self._build_tradingview_symbol()
        url = f"https://www.tradingview.com/conversation-status/?_rand={time.time()}&offset=0&room_id=general&stat_symbol={tv_symbol}&is_private="
        
        try:
            logger.info(f"💬 Fetching conversation status...")
            response = requests.get(url, headers=self.headers, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                
                sentiment_data = {
                    'timestamp': datetime.now().isoformat(),
                    'symbol': self.symbol,
                    'conversation_count': data.get('count', 0),
                    'active_users': data.get('active_users', 0),
                    'bullish_mentions': data.get('bullish', 0),
                    'bearish_mentions': data.get('bearish', 0),
                    'sentiment_score': self._calculate_sentiment_score(data),
                    'raw_data': data
                }
                
                logger.info(f"✅ Conversation data fetched")
                return sentiment_data
            else:
                logger.warning(f"⚠️ HTTP {response.status_code} for conversation")
                return {}
                
        except Exception as e:
            logger.error(f"❌ Error fetching conversation: {e}")
            return {}

    def _parse_news_item(self, item: Dict) -> Optional[Dict[str, Any]]:
        """پردازش یک خبر"""
        try:
            return {
                'id': item.get('id', ''),
                'title': item.get('title', ''),
                'published': item.get('published', ''),
                'source': item.get('provider', {}).get('name', 'Unknown'),
                'link': item.get('link', ''),
                'shortDescription': item.get('shortDescription', ''),
                'sentiment': self._analyze_sentiment(
                    item.get('title', '') + ' ' + item.get('shortDescription', '')
                ),
                'tags': item.get('tags', []),
                'fetchedAt': datetime.now().isoformat()
            }
        except Exception as e:
            logger.debug(f"Error parsing news item: {e}")
            return None

    def _parse_idea_item(self, item: Dict) -> Optional[Dict[str, Any]]:
        """پردازش یک ایده تحلیلی"""
        try:
            return {
                'id': item.get('id', ''),
                'title': item.get('title', ''),
                'author': item.get('author', {}).get('username', 'Unknown'),
                'imageUrl': item.get('imageUrl', ''),
                'description': item.get('description', ''),
                'likes': item.get('agree', 0),
                'comments': item.get('comments_count', 0),
                'isLong': item.get('is_long', None),
                'isShort': item.get('is_short', None),
                'publishedAt': item.get('publishedAt', ''),
                'sentiment': 'bullish' if item.get('is_long') else ('bearish' if item.get('is_short') else 'neutral'),
                'fetchedAt': datetime.now().isoformat()
            }
        except Exception as e:
            logger.debug(f"Error parsing idea item: {e}")
            return None

    def _analyze_sentiment(self, text: str) -> str:
        """
        تحلیل ساده سنتیمنت متن
        
        Args:
            text: متن برای تحلیل
            
        Returns:
            'bullish', 'bearish', یا 'neutral'
        """
        text_lower = text.lower()
        
        # کلمات کلیدی مثبت
        bullish_keywords = [
            'bullish', 'buy', 'long', 'surge', 'rally', 'gain', 'rise',
            'breakout', 'moon', 'pump', 'bull', 'growth', 'profit',
            'upgrade', 'partnership', 'adoption', 'positive'
        ]
        
        # کلمات کلیدی منفی
        bearish_keywords = [
            'bearish', 'sell', 'short', 'crash', 'dump', 'fall', 'drop',
            'breakdown', 'bear', 'loss', 'decline', 'downgrade',
            'risk', 'concern', 'negative', 'plunge'
        ]
        
        bullish_count = sum(1 for word in bullish_keywords if word in text_lower)
        bearish_count = sum(1 for word in bearish_keywords if word in text_lower)
        
        if bullish_count > bearish_count:
            return 'bullish'
        elif bearish_count > bullish_count:
            return 'bearish'
        else:
            return 'neutral'

    def _calculate_sentiment_score(self, data: Dict) -> float:
        """
        محاسبه امتیاز سنتیمنت (-1 تا +1)
        
        Args:
            data: داده‌های گفتگو
            
        Returns:
            امتیاز سنتیمنت
        """
        bullish = data.get('bullish', 0)
        bearish = data.get('bearish', 0)
        total = bullish + bearish
        
        if total == 0:
            return 0.0
        
        return (bullish - bearish) / total

    def generate_comprehensive_report(self) -> Dict[str, Any]:
        """
        تولید گزارش جامع اخبار فاندامنتال
        
        Returns:
            دیکشنری کامل با تمام اطلاعات
        """
        logger.info(f"📊 Generating comprehensive fundamental report for {self.symbol}...")
        
        # دریافت داده‌ها
        news = self.fetch_news_headlines()
        ideas = self.fetch_community_ideas()
        conversation = self.fetch_conversation_status()
        
        # تحلیل کلی سنتیمنت
        overall_sentiment = self._calculate_overall_sentiment(news, ideas, conversation)
        
        # ساخت گزارش
        report = {
            'metadata': {
                'symbol': self.symbol,
                'exchange': self.exchange,
                'base_currency': self.base_symbol,
                'generated_at': datetime.now().isoformat(),
                'timezone': 'UTC'
            },
            'news_headlines': {
                'total_count': len(news),
                'items': news,
                'sources': list(set([n['source'] for n in news if 'source' in n])),
                'sentiment_breakdown': self._sentiment_breakdown(news)
            },
            'community_ideas': {
                'total_count': len(ideas),
                'items': ideas,
                'sentiment_breakdown': self._sentiment_breakdown(ideas)
            },
            'conversation_status': conversation,
            'overall_analysis': {
                'sentiment': overall_sentiment['sentiment'],
                'sentiment_score': overall_sentiment['score'],
                'confidence': overall_sentiment['confidence'],
                'recommendation': overall_sentiment['recommendation'],
                'key_factors': overall_sentiment['factors']
            },
            'statistics': {
                'total_news': len(news),
                'total_ideas': len(ideas),
                'bullish_signals': overall_sentiment['bullish_count'],
                'bearish_signals': overall_sentiment['bearish_count'],
                'neutral_signals': overall_sentiment['neutral_count']
            }
        }
        
        logger.info(f"✅ Report generated: {overall_sentiment['sentiment'].upper()} sentiment")
        return report

    def _sentiment_breakdown(self, items: List[Dict]) -> Dict[str, int]:
        """تحلیل توزیع سنتیمنت"""
        breakdown = {'bullish': 0, 'bearish': 0, 'neutral': 0}
        
        for item in items:
            sentiment = item.get('sentiment', 'neutral')
            if sentiment in breakdown:
                breakdown[sentiment] += 1
        
        return breakdown

    def _calculate_overall_sentiment(
        self, 
        news: List[Dict], 
        ideas: List[Dict], 
        conversation: Dict
    ) -> Dict[str, Any]:
        """محاسبه سنتیمنت کلی با وزن‌دهی"""
        
        # شمارش سنتیمنت‌ها
        bullish = 0
        bearish = 0
        neutral = 0
        
        # وزن اخبار (40%)
        for item in news:
            sentiment = item.get('sentiment', 'neutral')
            if sentiment == 'bullish':
                bullish += 0.4
            elif sentiment == 'bearish':
                bearish += 0.4
            else:
                neutral += 0.4
        
        # وزن ایده‌ها (40%)
        for item in ideas:
            sentiment = item.get('sentiment', 'neutral')
            if sentiment == 'bullish':
                bullish += 0.4
            elif sentiment == 'bearish':
                bearish += 0.4
            else:
                neutral += 0.4
        
        # وزن گفتگوها (20%)
        conv_score = conversation.get('sentiment_score', 0)
        if conv_score > 0.2:
            bullish += 0.2
        elif conv_score < -0.2:
            bearish += 0.2
        else:
            neutral += 0.2
        
        total = bullish + bearish + neutral
        
        if total == 0:
            return {
                'sentiment': 'neutral',
                'score': 0.0,
                'confidence': 0.0,
                'recommendation': 'HOLD - داده کافی نیست',
                'factors': [],
                'bullish_count': 0,
                'bearish_count': 0,
                'neutral_count': 0
            }
        
        # نرمال‌سازی
        bullish_pct = bullish / total
        bearish_pct = bearish / total
        neutral_pct = neutral / total
        
        # تعیین سنتیمنت غالب
        if bullish_pct > 0.5:
            sentiment = 'bullish'
            score = bullish_pct - bearish_pct
            recommendation = 'BUY - سیگنال مثبت قوی'
        elif bearish_pct > 0.5:
            sentiment = 'bearish'
            score = bearish_pct - bullish_pct
            recommendation = 'SELL - سیگنال منفی قوی'
        elif abs(bullish_pct - bearish_pct) < 0.2:
            sentiment = 'neutral'
            score = 0.0
            recommendation = 'HOLD - سیگنال‌های متناقض'
        else:
            sentiment = 'neutral'
            score = bullish_pct - bearish_pct
            recommendation = 'HOLD - عدم اطمینان'
        
        # عوامل کلیدی
        factors = []
        if len(news) > 5:
            factors.append(f"{len(news)} خبر تازه منتشر شده")
        if len(ideas) > 3:
            factors.append(f"{len(ideas)} تحلیل کاربران")
        if conversation.get('conversation_count', 0) > 10:
            factors.append(f"{conversation.get('conversation_count')} گفتگوی فعال")
        
        confidence = min(0.95, (len(news) + len(ideas)) / 20)
        
        return {
            'sentiment': sentiment,
            'score': round(score, 3),
            'confidence': round(confidence, 2),
            'recommendation': recommendation,
            'factors': factors,
            'bullish_count': int(bullish),
            'bearish_count': int(bearish),
            'neutral_count': int(neutral)
        }

    def save_report_to_json(self, report: Dict[str, Any]) -> str:
        """
        ذخیره گزارش در فایل JSON
        
        Args:
            report: گزارش کامل
            
        Returns:
            مسیر فایل ذخیره‌شده
        """
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{self.symbol}_{timestamp}_fundamental.json"
        filepath = self.news_dir / filename
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2, ensure_ascii=False)
        
        logger.info(f"💾 Report saved to: {filepath}")
        return str(filepath)

    def get_latest_report(self) -> Optional[Dict[str, Any]]:
        """بارگذاری آخرین گزارش ذخیره‌شده"""
        try:
            json_files = list(self.news_dir.glob(f"{self.symbol}_*_fundamental.json"))
            if not json_files:
                return None
            
            latest_file = max(json_files, key=lambda p: p.stat().st_mtime)
            
            with open(latest_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"❌ Error loading report: {e}")
            return None


def main():
    """تست سیستم اخبار فاندامنتال"""
    
    # مثال 1: ADA
    print("\n" + "="*60)
    print("📰 Testing Fundamental News for ADAUSDT")
    print("="*60)
    
    analyzer = FundamentalNewsAnalyzer("ADAUSDT")
    report = analyzer.generate_comprehensive_report()
    filepath = analyzer.save_report_to_json(report)
    
    print(f"\n✅ Report saved: {filepath}")
    print(f"📊 Sentiment: {report['overall_analysis']['sentiment'].upper()}")
    print(f"💯 Confidence: {report['overall_analysis']['confidence']*100:.1f}%")
    print(f"📈 Recommendation: {report['overall_analysis']['recommendation']}")
    
    # مثال 2: SOL
    print("\n" + "="*60)
    print("📰 Testing Fundamental News for SOLUSDT")
    print("="*60)
    
    analyzer_sol = FundamentalNewsAnalyzer("SOLUSDT")
    report_sol = analyzer_sol.generate_comprehensive_report()
    filepath_sol = analyzer_sol.save_report_to_json(report_sol)
    
    print(f"\n✅ Report saved: {filepath_sol}")
    print(f"📊 Sentiment: {report_sol['overall_analysis']['sentiment'].upper()}")
    print(f"💯 Confidence: {report_sol['overall_analysis']['confidence']*100:.1f}%")
    print(f"📈 Recommendation: {report_sol['overall_analysis']['recommendation']}")


if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    main()
