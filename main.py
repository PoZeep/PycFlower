import sys
import PycFlowerTools


def main():
    if len(sys.argv) != 3:
        print("FORMAT: python3 main.py test.py 3")
        exit()
    else:
        filename = sys.argv[1]
        version = sys.argv[2]

    f = list(open(filename, "rb").read())
    file = PycFlowerTools.main(f, version)
    filename = 'obf_' + filename
    with open(filename, 'wb') as f:
        f.write(file)
    print("OK!")


if __name__ == "__main__":
    main()