from kivy.app import App
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.image import Image
from kivy.core.window import Window
from kivy.properties import ObjectProperty, NumericProperty, ListProperty, BooleanProperty
from kivy.core.image import Image as CoreImage
from kivy.core.image import ImageData
from kivy.lang import Builder
from kivy.uix.scatterlayout import ScatterLayout, Scatter
from kivy.uix.button import Button
from kivy.uix.popup import Popup


class TransformedImage(Image):
    def __init__(self, **kwargs):
        super(Image, self).__init__(**kwargs)
        self.bind(size=self.updateSize)
        self.bind(pos=self.updatePos)

    angle = NumericProperty(0)
    scaleX = NumericProperty(1)
    scaleY = NumericProperty(1)
    scaleXY = NumericProperty(1)

    pressed = ListProperty([0, 0])
    is_button = BooleanProperty(False)

    def on_touch_down(self, touch):
        if self.collide_point(*touch.pos) and self.is_button:
            self.pressed = touch.pos
            return True
        return super(TransformedImage, self).on_touch_down(touch)

    def on_pressed(self, instance, pos):
        print('pressed at {pos}; event consumed by {instance} with parent {parent}'.format(pos=pos, instance=instance,
                                                                                           parent=instance.parent))

    def updateSize(self, instance, *args):
        print(instance, "size:", self.size)
        print(instance.parent)

    def updatePos(self, instance, *args):
        print(instance, "pos:", self.pos)

    def on_angle(self, *args):
        widthWithRot = self.texture_size[1] if ((self.angle // 90) + 1) % 2 == 0 else self.texture_size[0]
        print("Rotation adjusted width", widthWithRot)

    def on_scaleX(self, *args):
        print("X scale is now:", self.scaleX)

    def on_scaleY(self, *args):
        print("Y scale is now:", self.scaleY)

    def on_scaleXY(self, *args):
        print("Self.texture_size:", self.texture_size)
        print("Window width:", str(Window.width) + ", self width:", self.texture_size[0])
        print("XY scale is now:", self.scaleXY)
        print("Self.width adjusted for scale:", self.texture_size[0] * self.scaleXY)


class TitleMenu(Button):
    def __init__(self, **kwargs):
        super(Button, self).__init__(**kwargs)


# Declare both screens
class TitleScreen(Screen):
    def __init__(self, **kwargs):
        super(TitleScreen, self).__init__(**kwargs)


class LoadingMainScreen(Screen):
    def __init__(self, **kwargs):
        super(LoadingMainScreen, self).__init__(**kwargs)


class HomeScreen(Screen):
    pass


class MenuPopup(Popup):
    pass


class fireemblem_copyApp(App):
    title = "Fire Emblem: Heroes"
    data = {}

    # 32 seems to be about the same as physical phone size (not pixel-wise!!!)
    scalefactor = 45
    Window.size = (9 * scalefactor, 16 * scalefactor)
    Window.left = 200
    Window.top = 40
    phone2WindowRatio = 0.28125

    def __init__(self, **kwargs):
        super(fireemblem_copyApp, self).__init__(**kwargs)

    def on_start(self):
        Window.bind(on_resize=self.on_window_resize)

    def on_window_resize(self, window, width, height):
        imSize = (self.root.get_screen('title').ids.myimage_title_bg.texture_size)
        scale = height / imSize[1]
        self.root.get_screen('title').ids.myscatter.size = list(map(lambda x: x * scale, imSize))
        print("Win Height:", str(height) + ", Texture Height:",
              str(self.root.get_screen('title').ids.myimage_title_bg.texture_size[1]))
        print("Myscatter size:", self.root.get_screen('title').ids.myscatter.size)

    def build(self):
        # Builder.load_file("fireemblem_copy.kv")

        # Create the screen manager
        sm = ScreenManager()
        sm.add_widget(TitleScreen(name='title'))
        sm.add_widget(LoadingMainScreen(name='loading_main'))

        return sm


if __name__ == '__main__':
    fireemblem_copyApp().run()
