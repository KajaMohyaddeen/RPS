import gb
import random
from kivy.app import App
from kivy.metrics import dp
from kivy.clock import Clock
from kivy.uix.image import Image
from kivy.uix.popup import Popup
from kivy.uix.button import Button
from kivy.uix.widget import Widget
from kivy.animation import Animation
from kivy.core.audio import SoundLoader
from kivy.properties import ObjectProperty, NumericProperty, StringProperty
from kivy.uix.screenmanager import ScreenManager, Screen, WipeTransition, RiseInTransition


class Blast(Image):
    pass


class MyPopup(Popup):
    """ window_ref refers Popup's parent class window(screen)
    reference through that we can call manager class to change current
    window and refresh the properties """

    window_ref = None

    def popup_open(self, window):

        self.window_ref = window

        if gb.user_points == 0 and gb.bot_points == 0:
            self.window_ref.transition = WipeTransition(duration=2)
            self.window_ref.transition.direction = 'left'
            self.window_ref.manager.current = 'infowindow'
        else:
            Clock.schedule_once(lambda dt: self.open(), .5)

    def popup_dismiss(self, status):
        scnd = self.window_ref.manager.get_screen('secondwindow')
        if status:
            scnd.refresh_properties()
            self.dismiss()
        else:
            self.dismiss()


class Rps(Button):
    anim = None

    def animate_rotate(self, ob):
        self.anim = Animation(angle=360)
        self.anim += Animation(angle=0)
        self.anim.repeat = True
        self.anim.start(ob)
        if ob.angle == 360:
            ob.angle = 0

    @staticmethod
    def on_angle(item, angle):
        if angle == 360:
            item.angle = 0


# This class will show the splash screen
class SplashWindow(Screen):
    rocket_anim = None
    event = None
    x = NumericProperty(.50)

    def on_enter(self):
        self.manager.sound.play()
        Clock.schedule_once(lambda x: self.animate_texts(), .1)

    def animate_texts(self):
        self.x += .35
        self.animate_move_texts(self.ids.text1)
        self.x += .10
        self.animate_move_texts(self.ids.text2)
        self.x += .15
        self.animate_move_texts(self.ids.text3)
        # animate flew rocket here
        self.animate_rocket()

    def animate_move_texts(self, ob):
        # anim = Animation(pos_hint={'center_x':ob.pos_hint.get('center_x'),'center_y':ob.pos_hint.get('center_y')})
        anim = Animation(
            pos_hint={'center_x': ob.pos_hint.get('center_x') + self.x, 'center_y': ob.pos_hint.get('center_y')}, d=.2)
        anim.start(ob)
        anim.bind(on_complete=lambda x, y: self.wiggle_text())

    def wiggle_text(self):
        anim = Animation(font_size=dp(25), d=.3)
        anim += Animation(font_size=dp(30), d=.3)
        anim.start(self.ids.text1)
        anim.start(self.ids.text2)
        anim.start(self.ids.text3)

    def animate_rocket(self):
        self.rocket_anim = Animation(pos_hint=self.ids.rocket.pos_hint)
        for i in range(1, 11):
            self.rocket_anim += Animation(pos_hint={'center_x': i * 0.1, 'center_y': i * 0.1}, d=.1)
        self.rocket_anim += Animation(opacity=0, d=.1)
        self.rocket_anim.start(self.ids.rocket)
        self.rocket_anim.bind(on_complete=lambda x, y: self.close_page())

    def close_page(self):
        self.event = Clock.schedule_interval(lambda dt: self.create_animation(), .1)

    def create_animation(self):
        # choices = ['clickblue.png','red.jpg','orange.jpeg','green.jpg','grey.png']
        choices = ['rock_sym', 'paper_sym', 'scissors_sym']
        for i in range(0, 30):
            ch = random.choice(choices)
            img = Image(source='Images/' + ch + '.jpg', size_hint=(.03, .03),
                        pos_hint={'center_x': (i * 0.08), 'center_y': self.my_y}, opacity=.8)

            self.add_widget(img)
            self.rain_animate(img)

        self.my_y += 0.045

        if self.my_y > 1.2:
            self.event.cancel()
            Clock.schedule_once(lambda dt: self.switch_to_home(), .3)

    def rain_animate(self, ob):
        anim = Animation(pos_hint={'center_y': self.my_y}, size_hint=(0.1, .1), opacity=1, duration=1)
        anim.start(ob)

    def switch_to_home(self):
        self.manager.transition = WipeTransition(duration=1)
        self.manager.transition.direction = 'left'
        self.manager.current = 'firstwindow'


# Points Choosing Window1
class InfoWindow(Screen):

    @staticmethod
    def assign_maxpoints(*args):
        scnd = App.get_running_app().root.get_screen('secondwindow')
        gb.max_points = args[1]
        scnd.ids.max_points_bar.text = str(gb.max_points)


# Home Window
class FirstWindow(Screen):

    @staticmethod
    def wiggle_once(ob):
        anim = Animation(size_hint=(ob.size_hint[0], ob.size_hint[1]), d=.1)
        anim += Animation(size_hint=(ob.size_hint[0] + 0.03, ob.size_hint[1] + 0.03), d=.1)
        anim += Animation(size_hint=(.2, .1))
        anim.start(ob)


# Game Window
class SecondWindow(Screen):
    sound = SoundLoader.load('Music/buttonclick.mp3')
    sound2 = SoundLoader.load('Music/blast.wav')
    user_progress = ObjectProperty(0)
    bot_progress = ObjectProperty(0)
    anim_event = None
    collision = None

    # while enter call wiggle function
    def on_enter(self):
        self.wiggle_func()

    # Wiggle Function to call wiggle animatiob
    def wiggle_func(self):
        items = [self.ids.rock, self.ids.paper, self.ids.scissors]

        if self.anim_event is None:
            for i in items:
                self.animate_wiggle(i)

    # Wiggle animation
    def animate_wiggle(self, ob):

        self.anim_event = Animation(size=(ob.size[0] + 20, ob.size[1] + 20), d=1)
        self.anim_event += Animation(size=(ob.size[0], ob.size[1]), d=1)
        self.anim_event.repeat = True
        self.anim_event.start(ob)

    # Animating Collision Blast with Sound
    def animate_collision(self, ob):

        # Blast image object
        # img = Image(source='Images/blast.png',size_hint=(.6,.4),pos_hint={'center_x':0.5,'center_y':0.7},opacity=0.5)

        self.collision = Animation(size_hint=(.4, .4), duration=0.2)
        self.collision &= Animation(pos_hint={'center_x': 0.5, 'center_y': 0.7}, duration=.1)

        # while both choices collide add blast image obj there at center  
        obj = Blast()
        self.collision.bind(on_complete=lambda x, y: self.ids.mainpanel.add_widget(obj))

        self.sound2.volume = 0.5
        self.sound2.play()

        if ob.text == 'usr':
            self.collision += Animation(pos_hint={'center_x': 0.2, 'center_y': 0.7}, opacity=0, duration=.5)

        if ob.text == 'bot':
            self.collision += Animation(pos_hint={'center_x': 0.8, 'center_y': 0.7}, opacity=0, duration=.5)

        self.collision += Animation(size_hint=(.2, .2), opacity=1, duration=0.2)
        self.collision.bind(on_complete=lambda x, y: self.break_time(obj))
        self.collision.start(ob)

    def break_time(self, obj):
        self.ids.mainpanel.remove_widget(obj)
        self.disable_options(False)

    # Refreshing The Properties of Game
    def refresh_properties(self):

        gb.user_points = 0
        gb.bot_points = 0
        self.user_progress = 0
        self.bot_progress = 0

        self.ids.userpoints.text = str(gb.user_points)
        self.ids.botpoints.text = str(gb.bot_points)
        self.ids.userchoice.source = 'Images/user.png'
        self.ids.botchoice.source = 'Images/bot.png'
        thrd = self.manager.get_screen('thirdwindow')
        thrd.ids.max_points.disabled = False

    #  Disable and Enable RPS buttons through function 
    def disable_options(self, status):

        self.ids.rock.disabled = status
        self.ids.paper.disabled = status
        self.ids.scissors.disabled = status

    def call_back(self, ob):

        thrd = self.manager.get_screen('thirdwindow')

        # self.sound.volume = thrd.ids.vol_slider.value / 4
        # self.sound.play()

        self.animate_collision(self.ids.userchoice)
        self.animate_collision(self.ids.botchoice)

        if gb.user_points < gb.max_points and gb.bot_points < gb.max_points:

            self.disable_options(True)

            choices = ['ROCK', 'PAPER', 'SCISSORS']
            gb.user_choice = ob.text  # Fetch the User Choice
            gb.bot_choice = random.choice(choices)  # Bot Take it Own Choice

            points = ['ROCKPAPER', 'PAPERSCISSORS', 'SCISSORSROCK']

            if gb.bot_choice + gb.user_choice in points:
                gb.user_points += 1

            elif gb.user_choice == gb.bot_choice:
                pass
            else:
                gb.bot_points += 1

            if gb.user_points != 0 or gb.bot_points != 0:
                thrd.ids.max_points.disabled = True

            self.ids.userpoints.text = str(gb.user_points)
            self.ids.botpoints.text = str(gb.bot_points)
            self.ids.userchoice.source = 'Images/' + gb.user_choice.lower() + '.png'
            self.ids.botchoice.source = 'Images/' + gb.bot_choice.lower() + '.png'

            self.user_progress = gb.user_points * 100 / gb.max_points
            self.bot_progress = gb.bot_points * 100 / gb.max_points

            if gb.user_points == gb.max_points:
                gb.result = 'USER'
                self.collision.bind(on_complete=lambda x, y: self.switch_to_fourth())

            if gb.bot_points == gb.max_points:
                gb.result = 'BOT'

                self.collision.bind(on_complete=lambda x, y: self.switch_to_fourth())

    def switch_to_fourth(self):
        self.manager.transition = RiseInTransition()
        self.manager.transition.direction = 'left'
        self.manager.current = 'fourthwindow'


# Settings Window


class ThirdWindow(Screen):
    count = 1
    src = StringProperty("")

    def __init__(self, **kwargs):
        super(ThirdWindow, self).__init__(**kwargs)
        self.app = App.get_running_app()

    def toggle(self):
        self.count += 1

        if self.count % 2 != 0:
            self.src = 'Images/unmute.png'
            self.music_stop()
        else:
            self.src = 'Images/mute.png'
            self.music_play()

    def music_play(self):
        self.app.bgsound.play()

    def music_stop(self):
        self.app.bgsound.stop()

    def volume(self, *args):
        self.app.bgsound.volume = args[1]

    def brightness(self, *args):
        self.app.root.opacity = args[1]
        # bg.set_brightness(args[1])


# Result window
class FourthWindow(Screen):
    def __init__(self, **kwargs):
        super(FourthWindow, self).__init__(**kwargs)
        self.success_sound = SoundLoader.load('Music/success.wav')
        self.failure_sound = SoundLoader.load('Music/failure.wav')

    def on_enter(self):
        self.animate_color(self.ids.layout)
        self.result_func()

    def animate_color(self, ob):

        anim = Animation(clr=(0, 0, 0, .6), d=.2)

        if gb.result == "USER":
            anim &= Animation(clr=(0, 1, 0, .6), d=1)
            self.success_sound.volume = .5
            self.success_sound.play()

        elif gb.result == "BOT":
            anim &= Animation(clr=(1, 0, 0, .6), d=1)
            self.failure_sound.play()
        else:
            pass
        anim += Animation(clr=(0, 0, 0, .6), d=1)
        anim.bind(on_complete=lambda x, y: self.go_home())

        anim.start(ob)

    def go_home(self):
        self.manager.current = 'firstwindow'

    def on_leave(self):
        self.ids.winner.text = '?'

    def result_func(self):
        self.ids.winner.text = gb.result


class FifthWindow(Screen):
    pass


class Progress(Widget):
    pass


class TransparentButton(Button):
    pass


class GameWindow(ScreenManager):
    pass


class Main(App):
    bgsound = SoundLoader.load('Music/bgmusic.wav')

    def build(self):
        self.bgsound.volume = 1
        return GameWindow()
    # if platform != "android":
    #     Layout = FloatLayout()
    #     Layout.add_widget(Label(text="ONLY SUPPORTED FOR ANDROID", pos_hint={'center_x': .5, 'center_y': .5},
    #                             font_name='Fonts/CaviarDreams.ttf'))
    #     return Layout


if __name__ == '__main__':
    Main().run()
