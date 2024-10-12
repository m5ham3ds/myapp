from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.spinner import Spinner
from kivy.uix.progressbar import ProgressBar
from kivy.uix.modalview import ModalView
from kivy.animation import Animation
import requests
from PIL import Image
import re
from bs4 import BeautifulSoup
import json
from io import BytesIO
from moviepy.editor import ImageSequenceClip, AudioFileClip, CompositeVideoClip, TextClip

class ContentCreationLayout(BoxLayout):
    def __init__(self, **kwargs):
        super(ContentCreationLayout, self).__init__(**kwargs)
        self.orientation = 'vertical'

        # شريط التحميل
        self.progress_bar = ProgressBar(max=100)
        self.add_widget(self.progress_bar)
        
        # حقل إدخال مفتاح جيميناي
        self.gemini_key = TextInput(hint_text='أدخل مفتاح Gemini / Enter Gemini Key', multiline=False)
        self.add_widget(self.gemini_key)
        
        # حقل إدخال مفتاح Eleven Labs
        self.eleven_key = TextInput(hint_text='أدخل مفتاح Eleven Labs / Enter Eleven Labs Key', multiline=False)
        self.add_widget(self.eleven_key)
        
        # حقل إدخال Voice ID
        self.voice_id = TextInput(hint_text='أدخل Voice ID / Enter Voice ID', multiline=False)
        self.add_widget(self.voice_id)        
                
        # قائمة منسدلة لاختيار أبعاد الصورة
        self.image_sizes = Spinner(
            text='اختر أبعاد الصورة / Select Image Size',
            values=["1080x1920", "1920x1080"]
        )
        self.add_widget(self.image_sizes)
        
        # قائمة منسدلة لاختيار نوع المحتوى
        self.content_types = Spinner(
            text='اختر نوع المحتوى / Select Content Type',
            values=[ "معلومات عامة انجليزي", "معلومات عامة عربي", "شرح مواقع تعمل بذكاء الاصطناعي", "أفكار و مقترحات لعمل محتوى على النت", "فيديوهات مضهكة ", "توب 10", "توب 5", "مراجعة هواتف", "مراجعة برامج", "قصص غامض ومثيرة", "قصص تحقيق وجريمه" ]
        )
        self.add_widget(self.content_types)
        
        # قسم الجدولة لاختيار مدة الفيديو
        schedule_layout = BoxLayout(orientation='horizontal')
        
        schedule_label = Label(text="حدد وقت عمل الفيديو / Set Video Duration", font_size='14sp', color=(1, 1, 1, 1))
        schedule_layout.add_widget(schedule_label)
        
        # قائمة منسدلة لاختيار الساعة
        self.hour_spinner = Spinner(
            text='ساعة / Hour',
            values=[f"{i:02}" for i in range(24)]
        )
        schedule_layout.add_widget(self.hour_spinner)
        
        # قائمة منسدلة لاختيار الدقيقة
        self.minute_spinner = Spinner(
            text='دقيقة / Minute',
            values=[f"{i:02}" for i in range(60)]
        )
        schedule_layout.add_widget(self.minute_spinner)
        
        self.add_widget(schedule_layout)
        
        # زر لإنشاء المحتوى
        self.create_btn = Button(text='إنشاء المحتوى / Create Content')
        self.create_btn.bind(on_press=self.create_content)
        self.add_widget(self.create_btn)
        
        # زر لحفظ الإعدادات
        self.save_btn = Button(text='حفظ الإعدادات / Save Settings')
        self.save_btn.bind(on_press=self.save_settings)
        self.add_widget(self.save_btn)

    def create_content(self, instance):
        # هنا يمكنك وضع منطق توليد المحتوى
        self.progress_bar.value = 10

        # إعداد مفاتيح API وتحديد نوع المحتوى
        gemini_api_key = self.gemini_key.text
        eleven_labs_api_key = self.eleven_key.text
        voice_id = self.voice_id.text
        content_type = self.content_types.text

        if not gemini_api_key or not eleven_labs_api_key or not voice_id:
            self.show_popup("تحذير / Warning", "يرجى إدخال جميع مفاتيح API و Voice ID. / Please enter all API keys and Voice ID.")
            return

        script = self.generate_script(gemini_api_key, content_type)
        if not script:
            self.show_popup("تحذير / Warning", "لا يوجد نص لتوليد المحتوى. / No script available for content generation.")
            return

        self.progress_bar.value = 30

        cleaned_script = self.clean_script(script)
        
        voiceover_filename = self.generate_voiceover(cleaned_script, eleven_labs_api_key, voice_id)
        if not voiceover_filename:
            self.show_popup("تحذير / Warning", "خطأ في توليد التعليق الصوتي. / Error generating voiceover.")
            return

        self.progress_bar.value = 50

        key_terms = self.extract_arabic_key_terms(cleaned_script)

        for term in key_terms:
            self.download_images_from_bing(term, num_images=2, folder="visual")

        self.progress_bar.value = 75

        try:
            self.create_video("visual", voiceover_filename)
            self.show_popup("نجاح / Success", "تم إنشاء المحتوى بنجاح! / Content created successfully!")
        except Exception as e:
            self.show_popup("خطأ / Error", f"حدث خطأ أثناء إنشاء الفيديو: {e} / An error occurred during video creation.")
        
        self.progress_bar.value = 100

    def save_settings(self, instance):
        # حفظ الإعدادات الحالية إلى ملف
        settings = {
            "gemini_key": self.gemini_key.text,
            "eleven_key": self.eleven_key.text,
            "voice_id": self.voice_id.text,
            "image_size": self.image_sizes.text,
            "content_type": self.content_types.text,
            "hour": self.hour_spinner.text,
            "minute": self.minute_spinner.text
        }
        with open('settings.json', 'w') as f:
            json.dump(settings, f)
        self.show_popup("نجاح / Success", "تم حفظ الإعدادات بنجاح! / Settings saved successfully!")

    def show_popup(self, title, message):
        # استخدام ModalView لعرض الإشعارات بشكل أفضل
        view = ModalView(size_hint=(0.8, 0.4))
        content = BoxLayout(orientation='vertical', padding=10)
        label = Label(text=message, halign='center', valign='middle')
        label.bind(size=label.setter('text_size'))  # ضبط حجم النص ليكون بمحاذاة صحيحة
        content.add_widget(label)
        close_button = Button(text='إغلاق / Close', size_hint=(1, 0.2))
        close_button.bind(on_press=view.dismiss)
        content.add_widget(close_button)
        view.add_widget(content)

        # إضافة تأثير حركة للنافذة
        animation = Animation(opacity=1, duration=0.3) + Animation(opacity=0.5, duration=0.3)
        animation.repeat = True
        animation.start(view)

        view.open()

    def generate_script(self, api_key, content_type):
        # استخدام خريطة النصوص لتوليد النص المطلوب بناءً على نوع المحتوى
        prompt_map = {
                "معلومات عامة انجليزي": "Well, connect all search engines in the world and write me a script in English, talking about information, discoveries, civilizations, technology, customs, companies, businesses and projects in a professional manner. Also, make the beginning of the video enthusiastic and exciting to attract the viewer. And I finished the video by inviting the viewer to like the video and subscribe to the channel.",
    "معلومات عامة عربي": "Well, connect all search engines in the world and write me a script in Arabic, talking about information, discoveries, civilizations, technology, customs, companies, businesses and projects in a professional manner. Also, make the beginning of the video enthusiastic and exciting to attract the viewer. And I finished the video by inviting the viewer to like the video and subscribe to the channel.", 
    "شرح مواقع تعمل بذكاء الاصطناعي": "Well, connect all search engines in the world and write me a script in English, talking about an artificial intelligence site, to make a video montage, create a full website, blogs, write an article, and create professional posts in a professional way. Also, make the beginning of the video enthusiastic and exciting to attract the viewer. And I finished the video by inviting the viewer to like the video and subscribe to the channel.", 
    "أفكار و مقترحات لعمل محتوى على النت": "Well, connect all the search engines in the world and write me a script in English that talks about ideas and suggestions for creating content on the Internet and social media platforms in a professional way. Also, make the beginning of the video enthusiastic and exciting to attract the viewer. And I finished the video by inviting the viewer to like the video and subscribe to the channel.",  
    "فيديوهات ههه": "Well, connect all the search engines in the world and write me a script in English, talking about funny and fun videos in a professional way. Also, make the beginning of the video enthusiastic and exciting to attract the viewer. And I finished the video by inviting the viewer to like the video and subscribe to the channel.",
    "توب 10": "Well, connect all the search engines in the world and write me a script in English. It talks about making top10 videos. One of the top ten things, for example, are the top ten projects, the best ten Cyprus, the best ten cars, the best ten buildings in the world or the best. Ten airports and so on professionally. Also, make the beginning of the video enthusiastic and exciting to attract the viewer. And I finished the video by inviting the viewer to like the video and subscribe to the channel.",
    "توب 5": "Well, connect all search engines in the world and write me a script in English. It talks about making top5 videos. One of the top five things. Airports and so on professionally. Also, make the beginning of the video enthusiastic and exciting to attract the viewer. And I finished the video by inviting the viewer to like the video and subscribe to the channel.",
    "مراجعة هواتف": "Well, connect all the search engines in the world and write me a script in English, talking about a review of the new phones and computers. Every time I update the text, I make a different phone or computer references in a professional way. Also, make the beginning of the video enthusiastic and exciting to attract the viewer. And I finished the video by inviting the viewer to like the video and subscribe to the channel.",  
    "مراجعة برامج": "Well, connect all search engines in the world and write me a script in English, talking about making videos, explaining different and new programs and applications in a professional way. Also, make the beginning of the video enthusiastic and exciting to attract the viewer. And I finished the video by inviting the viewer to like the video and subscribe to the channel.", 
    "قصص غامض ومثيرة": "Well, connect all the search engines in the world and write me a script in English that talks about making mysterious and exciting stories that contain mystery and an exciting plot in a professional way. Also, make the beginning of the video enthusiastic and exciting to attract the viewer. And I finished the video by inviting the viewer to like the video and subscribe to the channel.",
    "قصص تحقيق وجريمه": "Well, connect all the search engines in the world and write me a script in English that talks about making investigation stories and a crime that contains mystery and an exciting plot in a professional way. Also, make the beginning of the video enthusiastic and exciting to attract the viewer. And I finished the video by inviting the viewer to like the video and subscribe to the channel.",
            # بقية الخريطة...
        }
        prompt = prompt_map.get(content_type)
        if not prompt:
            return ""
        return prompt

    def clean_script(self, script):
        # تنظيف النص من التعليمات المشهدية
        lines = script.split('\n')
        cleaned_lines = [line for line in lines if not any(word in line.lower() for word in ['مشهد', 'صورة', 'لقطة'])]
        return '\n'.join(cleaned_lines)

    def generate_voiceover(self, script, api_key, voice_id):
        # توليد التعليق الصوتي باستخدام Eleven Labs API
        try:
            url = f"https://api.elevenlabs.io/v1/text-to-speech/{voice_id}"
            headers = {
                "Accept": "audio/mpeg",
                "Content-Type": "application/json",
                "xi-api-key": api_key
            }
            data = {
                "text": script,
                "model_id": "eleven_multilingual_v2",
                "voice_settings": {
                    "stability": 0.5,
                    "similarity_boost": 0.5
                }
            }
            response = requests.post(url, json=data, headers=headers)
            response.raise_for_status()
            output_audio_filename = 'arabic_voiceover.mp3'
            with open(output_audio_filename, 'wb') as f:
                for chunk in response.iter_content(chunk_size=1024):
                    if chunk:
                        f.write(chunk)
            return output_audio_filename
        except Exception as e:
            self.show_popup("خطأ / Error", f"Error generating voiceover: {e}")
            return None

    def extract_arabic_key_terms(self, script):
        # استخراج المصطلحات الأساسية من النص
        words = re.findall(r'\b[\u0600-\u06FF]+\b', script)
        return list(set(words))

    def download_images_from_bing(self, query, num_images, folder):
        # تنزيل الصور من Bing
        try:
            headers = {"User-Agent": "Mozilla/5.0"}
            search_url = f"https://www.bing.com/images/search?q={query}&FORM=HDRSC2"
            response = requests.get(search_url, headers=headers)
            response.raise_for_status()
            soup = BeautifulSoup(response.text, 'html.parser')
            image_elements = soup.find_all('a', {'class': 'iusc'})

            os.makedirs(folder, exist_ok=True)
            image_count = 0

            for i, img_element in enumerate(image_elements):
                if image_count >= num_images:
                    break
                m = img_element.get('m')
                if m:
                    m = json.loads(m)
                    img_url = m['murl']

                    if img_url:
                        try:
                            img_data = requests.get(img_url, headers=headers, timeout=10).content
                            img = Image.open(BytesIO(img_data))
                            img = self.resize_and_crop_image(img)
                            img_filename = os.path.join(folder, f'image_{image_count + 1}.png')
                            img.save(img_filename, format='PNG', quality=95)
                            image_count += 1
                            print(f"Downloaded {img_filename}")
                        except Exception as e:
                            print(f"Failed to download image {i + 1}: {e}")

        except Exception as e:
            self.show_popup("خطأ / Error", f"Error downloading images: {e}")

    def resize_and_crop_image(self, img):
        selected_size = self.image_sizes.text
        target_size = (1080, 1920) if selected_size == "1080x1920" else (1920, 1080)

        img_ratio = img.width / img.height
        target_ratio = target_size[0] / target_size[1]

        if img_ratio > target_ratio:
            new_width = int(img.height * target_ratio)
            left = (img.width - new_width) // 2
            img = img.crop((left, 0, left + new_width, img.height))
        else:
            new_height = int(img.width / target_ratio)
            top = (img.height - new_height) // 2
            img = img.crop((0, top, img.width, top + new_height))

        img = img.resize(target_size, Image.LANCZOS)
        return img

    def create_video(self, image_folder, audio_filename):
        # إنشاء الفيديو مع الصوت والصور
        try:
            image_files = [os.path.join(image_folder, img) for img in os.listdir(image_folder) if img.endswith(".png")]
            clip = ImageSequenceClip(image_files, fps=1)
            audio = AudioFileClip(audio_filename)
            video_duration = int(self.hour_spinner.text) * 3600 + int(self.minute_spinner.text) * 60
            
            subtitles = [
                {"text": "الترجمة الأولى هنا / First subtitle here", "start": 0, "end": 3},
                {"text": "الترجمة الثانية هنا / Second subtitle here", "start": 3, "end": 6},
            ]
            
            subtitle_clips = []
            for subtitle in subtitles:
                txt_clip = TextClip(subtitle["text"], fontsize=24, color='white', bg_color='black')
                txt_clip = txt_clip.set_position(('center', 'bottom')).set_start(subtitle["start"]).set_duration(subtitle["end"] - subtitle["start"])
                subtitle_clips.append(txt_clip)
            
            video_with_subtitles = CompositeVideoClip([clip] + subtitle_clips).set_duration(video_duration).set_audio(audio)
            video_with_subtitles.write_videofile("output_video.mp4", codec="libx264", audio_codec="aac")
            
        except Exception as e:
            self.show_popup("خطأ / Error", f"Error creating video: {e}")

class ContentCreationApp(App):
    def build(self):
        return ContentCreationLayout()

if __name__ == '__main__':
    ContentCreationApp().run()