import api.db as db
from api.banner import Banner, BannerImage
import api.blob.sample

sess = db.Session()

sess.add(Banner(alt="CSES!", images=[
	BannerImage(blob="BF263BDFE95CBD9101C3AE769B2F93A10AE576D6", width=619, height=183),
	BannerImage(blob="12DC7B0D61D0943E0E862A55911ABA43619EA371", width=200, height=200),
]))

sess.add(Banner(alt="Summer Directorship Applications Now Open",
                href="/directorships", images=[
	BannerImage(blob="B963C4AEE97D58F264B62E5F61E7829DEA94332F", width=647, height=253),
]))

sess.add(Banner(alt="Summer Directorship Applications Now Open",
                href="/directorships", path="/directorships", images=[
	BannerImage(blob="B963C4AEE97D58F264B62E5F61E7829DEA94332F", width=647, height=253),
]))

sess.commit()
