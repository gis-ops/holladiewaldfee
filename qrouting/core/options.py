class STYLES:
    class LINE:
        SIZE = 1

    class POINT:
        WIDTH = 2

    class ANNOTATION:
        WIDTH = 5
        HEIGHT = 8
        OFFSET_X = 5
        OFFSET_Y = 5

    @staticmethod
    def annotation_html(idx: int) -> str:
        return "<strong>" + str(idx) + "</strong>"
