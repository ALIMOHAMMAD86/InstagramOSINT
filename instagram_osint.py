#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Instagram OSINT Tool - Python Version
استخراج اطلاعات پروفایل Instagram
"""

import requests
import json
import sys
from datetime import datetime
from pathlib import Path

class InstagramOSINT:
    def __init__(self):
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        }
        self.session = requests.Session()
        self.session.headers.update(self.headers)

    def fetch_profile(self, username):
        """
        روش 1: استفاده از Instagram Web API
        """
        try:
            url = f'https://www.instagram.com/api/v1/users/web_profile_info/?username={username}'
            response = self.session.get(url, timeout=10)
            
            if response.status_code == 200:
                return response.json()['data']['user']
            else:
                return None
        except Exception as e:
            print(f"❌ روش 1 ناموفق: {str(e)}")
            return None

    def fetch_profile_graphql(self, username):
        """
        روش 2: استفاده از Instagram GraphQL
        """
        try:
            # ابتدا صفحه رو بارگذاری کن تا shared_data رو گرفت
            page_url = f'https://www.instagram.com/{username}/'
            response = self.session.get(page_url, timeout=10)
            
            if 'window._sharedData' in response.text:
                # استخراج JSON از صفحه
                start = response.text.find('window._sharedData = ') + len('window._sharedData = ')
                end = response.text.find('};', start) + 1
                
                if start > len('window._sharedData = ') - 1 and end > start:
                    json_str = response.text[start:end]
                    data = json.loads(json_str)
                    
                    # اطلاعات کاربر از GraphQL
                    user_data = data.get('props', {}).get('pageProps', {}).get('userDetails', {})
                    if user_data:
                        return user_data
                    
                    # یا از entry_data
                    entry_data = data.get('entry_data', {})
                    if 'ProfilePage' in entry_data:
                        user = entry_data['ProfilePage'][0]['graphql']['user']
                        return user
            
            return None
        except Exception as e:
            print(f"❌ روش 2 ناموفق: {str(e)}")
            return None

    def fetch_profile_alternative(self, username):
        """
        روش 3: استفاده از API جایگزین
        """
        try:
            # استفاده از Instagram's public GraphQL endpoint
            query_hash = "c9100bf08aaf7a52bda2ff002928dd"
            variables = json.dumps({"user_id": username})
            
            url = 'https://www.instagram.com/graphql/query/'
            params = {
                'query_hash': query_hash,
                'variables': variables
            }
            
            response = self.session.get(url, params=params, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                if 'data' in data:
                    return data['data'].get('user')
            
            return None
        except Exception as e:
            print(f"❌ روش 3 ناموفق: {str(e)}")
            return None

    def search_user(self, username):
        """
        جستجو برای کاربر
        """
        try:
            url = f'https://www.instagram.com/api/v1/web/search/topsearch/?query={username}'
            response = self.session.get(url, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                if 'users' in data and len(data['users']) > 0:
                    return data['users'][0]['user']
            
            return None
        except Exception as e:
            print(f"❌ جستجو ناموفق: {str(e)}")
            return None

    def get_user_info(self, username):
        """
        دریافت اطلاعات کاربر - تمام روش‌ها رو سعی کن
        """
        print(f"\n🔍 جستجو برای: @{username}")
        print("=" * 50)
        
        # سعی کن روش 1
        print("⏳ درحال سعی روش 1 (API رسمی)...")
        user_data = self.fetch_profile(username)
        
        if not user_data:
            # سعی کن روش 2
            print("⏳ درحال سعی روش 2 (GraphQL)...")
            user_data = self.fetch_profile_graphql(username)
        
        if not user_data:
            # سعی کن روش 3
            print("⏳ درحال سعی روش 3 (جستجو)...")
            user_data = self.search_user(username)
        
        if not user_data:
            print("⏳ درحال سعی روش 4 (صفحه اصلی)...")
            user_data = self.fetch_profile_alternative(username)
        
        return user_data

    def display_results(self, user_data):
        """
        نمایش اطلاعات کاربر
        """
        if not user_data:
            print("❌ پروفایل یافت نشد!")
            return False

        print("\n✅ اطلاعات دریافت شد!")
        print("=" * 50)
        
        # استخراج اطلاعات
        username = user_data.get('username', 'N/A')
        full_name = user_data.get('full_name', 'N/A')
        biography = user_data.get('biography', 'بیوگرافی ندارد')
        followers = user_data.get('follower_count', 0)
        following = user_data.get('following_count', 0)
        media_count = user_data.get('media_count', 0)
        is_verified = user_data.get('is_verified', False)
        is_private = user_data.get('is_private', False)
        is_business = user_data.get('is_business_account', False)
        external_url = user_data.get('external_url', 'ندارد')
        business_category = user_data.get('business_category_name', 'N/A')
        profile_pic_url = user_data.get('profile_pic_url_hd', 'N/A')
        
        # نمایش اطلاعات
        print(f"\n👤 نام کاربری: @{username}")
        print(f"📝 نام کامل: {full_name}")
        print(f"\n📊 آمار:")
        print(f"   👥 دنبال‌کننده‌ها: {followers:,}")
        print(f"   👉 دنبال‌کردن‌ها: {following:,}")
        print(f"   📸 پست‌ها: {media_count}")
        
        print(f"\n🏷️  برچسب‌ها:")
        print(f"   ✓ تایید شده: {'✅ بله' if is_verified else '❌ خیر'}")
        print(f"   🔒 حساب خصوصی: {'✅ بله' if is_private else '❌ خیر'}")
        print(f"   💼 حساب تجاری: {'✅ بله' if is_business else '❌ خیر'}")
        
        print(f"\n📄 بیوگرافی:")
        print(f"   {biography}")
        
        if external_url != 'ندارد':
            print(f"\n🔗 لینک خارجی: {external_url}")
        
        if business_category != 'N/A':
            print(f"\n🏢 دسته تجاری: {business_category}")
        
        print(f"\n🖼️  تصویر پروفایل: {profile_pic_url}")
        print(f"\n📱 لینک پروفایل: https://instagram.com/{username}/")
        
        return True

    def save_results(self, username, user_data):
        """
        ذخیره نتایج در فایل JSON
        """
        if not user_data:
            return False
        
        try:
            # ایجاد پوشه نتایج
            results_dir = Path('instagram_results')
            results_dir.mkdir(exist_ok=True)
            
            # نام فایل
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = results_dir / f'{username}_{timestamp}.json'
            
            # ذخیره JSON
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(user_data, f, ensure_ascii=False, indent=2)
            
            print(f"\n💾 نتایج ذخیره شد: {filename}")
            return True
        except Exception as e:
            print(f"❌ خطا در ذخیره: {str(e)}")
            return False


def main():
    """
    برنامه اصلی
    """
    print("""
    ╔══════════════════════════════════════╗
    ║  📸 Instagram OSINT Tool - Python    ║
    ║     اطلاعات پروفایل Instagram       ║
    ╚══════════════════════════════════════╝
    """)
    
    # بررسی نام کاربری
    if len(sys.argv) > 1:
        username = sys.argv[1].replace('@', '')
    else:
        username = input("🔍 نام کاربری Instagram را وارد کنید (بدون @): ").strip().replace('@', '')
    
    if not username:
        print("❌ نام کاربری الزامی است!")
        sys.exit(1)
    
    # ایجاد نمونه و شروع جستجو
    osint = InstagramOSINT()
    user_data = osint.get_user_info(username)
    
    # نمایش نتایج
    if osint.display_results(user_data):
        # ذخیره نتایج
        save = input("\n💾 آیا نتایج ذخیره شود؟ (بله/خیر): ").lower()
        if save in ['بله', 'yes', 'y', 'ب']:
            osint.save_results(username, user_data)
    
    print("\n" + "=" * 50)
    print("✅ کار تمام شد!")


if __name__ == '__main__':
    main()
