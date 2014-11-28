class FourLewds(object):
    def __init__(self):
        sys.path.insert(0, './lewd/src')
        from remotescreen import RemoteScreen
        self.w = 10
        self.h = 12
        self.screen = RemoteScreen(LEWDWALL_IP, LEWDWALL_PORT,
            dimension=(self.w,self.h))

        f = [[(0, 0, 0) for y in range(self.h)] for x in range(self.w)]
        self.screen.load_frame(f)
        self.screen.push()

    def write(self, freq):
        fr = [freq[10 * (i + 1)] for i in xrange(12)]
        f = [[(0, 0, 0) for y in range(self.h)] for x in range(self.w)]

        def fill_bar(bar, fill):
            for idx in range(fill):
                f[9 - idx][bar] = (0, 30, 75)

        for ind, frq in enumerate(fr):
            #frq =frq*75
            frq =frq*25
            bars = int(round(min(frq, 10)))

            fill_bar(ind, bars)

        self.screen.load_frame(f)
        self.screen.push()
