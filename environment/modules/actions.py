class EnvActions:
    def press(self, key):
        pass

    def Right(self):
        return "Right"

    def Left(self):
        return "Left"

    def Top(self):
        return "Up"

    def Bottom(self):
        return "Down"

    def doNothing(self):
        return ""

    def resetServo(self):
        return "V"

    def RESET(self):
        return "R"

    def get_actions(self):
        return ["Right", "Left", "Top", "Bottom"]

    def get_action(self, _index):
        actions = self.get_actions()
        key = actions[_index]
        keystroke = None

        if key=="Right":
            keystroke = self.Right()
        elif key=="Left":
            keystroke = self.Left()
        elif key=="Top":
            keystroke = self.Top()
        elif key=="Bottom":
            keystroke = self.Bottom()
        elif key=="doNothing":
            keystroke = self.doNothing()
        elif key=="resetServo":
            keystroke = self.resetServo()
        elif key=="reset":
            keystroke = self.RESET()

        return keystroke

