from typing import Optional, List

from cli.args import parse_args
from core.logging import setup_logging, get_logger

logger = get_logger("static_analysis_assistant")


def perform_analysis(deep: bool, targets: List[str]) -> None:
    mode = "deep" if deep else "normal"
    logger.info(f"Running {mode} analysis on: {', '.join(targets)}")
    logger.debug("Analysis logic not implemented yet.")


def main(argv: Optional[List[str]] = None) -> None:
    args = parse_args(argv)
    setup_logging(args.verbose)

    targets: List[str] = []
    if args.ui:
        targets.append("ui")
    if args.back:
        targets.append("back")

    if not targets:
        # targets = ["ui", "back"]
        print("No targets provided")
        return

    perform_analysis(args.deep_analyze, targets)