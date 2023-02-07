from src.magmail import Magmail

data = Magmail(
  "sample_mbox/star.mbox",
  auto_clean=True,
  filter_content_type="text/plain"
)
