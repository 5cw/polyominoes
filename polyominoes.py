from matplotlib import pyplot as plt, patches
import pandas as pd


cmap = plt.get_cmap('hsv', 100)

def norm(squares):
    xs, ys = zip(*squares)
    return {(x - min(xs), y - min(ys)) for x, y in squares}
def rot(squares):
    return norm([(-y, x) for x, y in squares])

def flip(squares):
    return norm([(-x, y) for x, y in squares])

def bitrep(squares):
    return sum(1 << x + y * 8 for x, y in squares)

def decode_bitrep(b):
    sq = set()
    for i in range(64):
        y, x = divmod(i, 8)
        if b >> i & 1:
            sq.add((x, y))
    return sq
class Polyomino:
    squares: set[(int, int)]
    rots: list[int]
    draw_rot: int
    name: str

    def __init__(self, squares, name=''):
        if not isinstance(squares, int):
            self.squares = norm(squares)
        else:
            self.squares = decode_bitrep(squares)
        r1 = rot(self.squares)
        r2 = rot(r1)
        r3 = rot(r2)
        self.rots = [*map(bitrep, [self.squares, r1, r2, r3])]
        self.draw_rot = 0
        self.name = name

    def extensions(self):
        checked = set(self.squares)
        out = []
        for x, y in self.squares:
            for dx, dy in [(0, 1), (0, -1), (1, 0), (-1, 0)]:
                nx, ny = x + dx, y + dy
                if (nx, ny) not in checked:
                    out.append(Polyomino(self.squares | {(nx, ny)}))
                    checked.add((nx, ny))
        return out


    def __eq__(self, other):
        return other.rots[0] in self.rots

    def __repr__(self):
        return str(self.squares)

    def get_color(self):
        flp = Polyomino(flip(self.squares))
        rots = flp.rots + self.rots
        return cmap(pow(max(rots),min(rots),97))
    def draw(self, ax, n):
        sq = self.squares
        for i in range(self.draw_rot):
            sq = rot(sq)
        xs, ys = zip(*sq)
        mx, my = max(xs) + 1, max(ys) + 1
        cx, cy = mx / 2, my / 2
        color = self.get_color()
        for x, y in sq:
            ax.add_patch(patches.Rectangle((x - cx, y - cy), 1, 1, facecolor=color, edgecolor='black'))
        ax.set_axis_off()
        size = max(3.5, (n + 1)/2)
        ax.set_xlim(-size, size)
        ax.set_ylim(-size, size)
        ax.set_title(f'{self.name}', y=-max(.2, n/20 - .1))

PREFIXES = ['null', 'mon', 'd', 'tri', 'tetr', 'pent', 'hex', 'sept', 'oct']


def get_name(n):
    return PREFIXES[n] + 'omino'


def generate(n: int, keep: bool, file=None):
    nominoes = [Polyomino([(0, 0)])]
    for _ in range(n - 1):
        #print(_)
        newnominoes = []
        for p in nominoes:
            for x in p.extensions():
                if x not in newnominoes and x not in nominoes:
                    newnominoes.append(x)
        if not keep:
            nominoes = newnominoes
        else:
            nominoes += newnominoes
    #print(nominoes, len(nominoes))

    if file is None:
        file = get_name(n)

    try:
        df = pd.read_csv(f'data/{file}es.csv')
        df.fillna(0, inplace=True)
    except FileNotFoundError:
        df = pd.DataFrame(columns=['name', 'rot', 'main'])
    sv = pd.DataFrame(columns=['name', 'bitrep'])

    used = set()
    for i, nomino in enumerate(nominoes):
        nomino.draw_rot = int(df['rot'].get(i, 0))
        nomino.name = df['name'].get(i, "none")
    idx = 0
    for i, nomino in enumerate(nominoes):
        if not df['main'].get(i, 0):
            continue

        f = bitrep(flip(nomino.squares))
        for j, o in enumerate(nominoes):
            if f in o.rots:
                sv.loc[idx] = [nomino.name, nomino.rots[nomino.draw_rot]]
                sv.loc[idx + 1] = [o.name, o.rots[o.draw_rot]]
                used |= {i, j}
                idx += 2

    for i, nomino in enumerate(nominoes):
        if i in used:
            continue
        sv.loc[idx] = [nomino.name, nomino.rots[nomino.draw_rot]]
        idx += 1
    sv['bitrep'] = sv['bitrep'].astype(int)
    sv.to_csv(f'data/{file}_data.csv', index=False)

def make_image(n, file=None):
    rows, cols = [(0, 0), (1, 1), (1, 1), (1, 4), (1, 7), (3, 6), (6, 10), (28, 7)][n]

    bfig, axs = plt.subplots(rows, cols, figsize=(cols, rows), dpi=300)
    if file is None:
        file = get_name(n)
    sv = pd.read_csv(f'data/{file}_data.csv')

    for i, [name, b] in sv.iterrows():
        #print(i, name)
        i = int(i if name not in [0, 1, 2, 3, 4, 5, 6] else name)

        p = Polyomino(int(b), name)
        if rows == 1:
            ax = axs[i]
        else:
            ax = axs[i // cols, i % cols]
        ax.set_aspect('equal')
        p.draw(ax, n)
    bfig.savefig(f'images/{file}es.png',bbox_inches='tight')

generate(3, True)
make_image(3)
generate(4, False, 'tetris')
make_image(4, 'tetris')
generate(4, False)
make_image(4)
generate(5, False)
make_image(5)
generate(6, False)
make_image(6)