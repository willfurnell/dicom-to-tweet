import tweepy
from config import *
from pynetdicom import AE, debug_logger, evt, AllStoragePresentationContexts, ALL_TRANSFER_SYNTAXES
import numpy as np
import io
from PIL import Image

client = tweepy.Client(
    consumer_key=CONSUMER_KEY,
    consumer_secret=CONSUMER_SECRET,
    access_token=ACCESS_TOKEN,
    access_token_secret=ACCESS_TOKEN_SECRET
)

v1_api = tweepy.OAuth1UserHandler(
    consumer_key=CONSUMER_KEY,
    consumer_secret=CONSUMER_SECRET,
    access_token=ACCESS_TOKEN,
    access_token_secret=ACCESS_TOKEN_SECRET
)

debug_logger()

def handle_store(event):
    """Handle EVT_C_STORE events."""
    ds = event.dataset
    ds.file_meta = event.file_meta

    # From this issue: https://github.com/pydicom/pydicom/issues/352#issuecomment-406767850
    # Convert to float to avoid overflow or underflow losses.
    image_2d = ds.pixel_array.astype(float)

    # Rescaling grey scale between 0-255
    image_2d_scaled = (np.maximum(image_2d,0) / image_2d.max()) * 255.0

    # Convert to uint
    image_2d_scaled = np.uint8(image_2d_scaled)

    image_buffer = io.BytesIO()

    # Seek to the beginning of the buffer
    image_buffer.seek(0)
    im = Image.fromarray(image_2d_scaled)
    im.save(image_buffer, format="JPEG")
    # We need to go to the start afterwards for the upload
    image_buffer.seek(0)
    
    # Annoyingly, Twitter's V2 API does not yet support uploading images!?!...
    api = tweepy.API(v1_api)
    media = api.media_upload(filename="temp.png", file=image_buffer)

    # ...But you have to use the V2 API to tweet...
    client.create_tweet(text=TWEET, media_ids=[media.media_id])
    return 0x0000


# Heavily influenced by the example docs: https://pydicom.github.io/pynetdicom/stable/examples/storage.html#storage-scp

handlers = [(evt.EVT_C_STORE, handle_store)]

ae = AE()

storage_sop_classes = [cx.abstract_syntax for cx in AllStoragePresentationContexts]

for uid in storage_sop_classes:
    ae.add_supported_context(uid, ALL_TRANSFER_SYNTAXES)

# Make sure you appropriate
ae.start_server((ADDRESS, PORT), block=True, evt_handlers=handlers)

