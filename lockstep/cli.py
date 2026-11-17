import argparse
import lockstep as m


def main():
    ap = argparse.ArgumentParser(description="帧同步确定性")
        ap.add_argument("--frames", type=int, default=30)
        ap.add_argument("--out", required=True)
    a = ap.parse_args()
        print("TODO")


if __name__ == "__main__":
    main()
