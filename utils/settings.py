import os
CHROME_DRIVER_PATH = 'webdriver/chromedriver'
session_user = os.getlogin()
CHROME_PROFILE = f"user-data-dir=/home/{session_user}/.config/google-chrome/whatsapp_test"
# CHROME_PROFILE = f"user-data-dir=/home/{session_user}/.config/google-chrome/whatsapp_tests"
XHR_SCRIPT = '''
var uri = arguments[0];
var callback = arguments[1];
var toBase64 = function (buffer) {
  for (
    var r,
      n = new Uint8Array(buffer),
      t = n.length,
      a = new Uint8Array(4 * Math.ceil(t / 3)),
      i = new Uint8Array(64),
      o = 0,
      c = 0;
    64 > c;
    ++c
  )
    i[c] =
      "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/".charCodeAt(
        c
      );
  for (c = 0; t - (t % 3) > c; c += 3, o += 4)
    (r = (n[c] << 16) | (n[c + 1] << 8) | n[c + 2]),
      (a[o] = i[r >> 18]),
      (a[o + 1] = i[(r >> 12) & 63]),
      (a[o + 2] = i[(r >> 6) & 63]),
      (a[o + 3] = i[63 & r]);
  return (
    t % 3 === 1
      ? ((r = n[t - 1]),
        (a[o] = i[r >> 2]),
        (a[o + 1] = i[(r << 4) & 63]),
        (a[o + 2] = 61),
        (a[o + 3] = 61))
      : t % 3 === 2 &&
        ((r = (n[t - 2] << 8) + n[t - 1]),
        (a[o] = i[r >> 10]),
        (a[o + 1] = i[(r >> 4) & 63]),
        (a[o + 2] = i[(r << 2) & 63]),
        (a[o + 3] = 61)),
    new TextDecoder("ascii").decode(a)
  );
};
var xhr = new XMLHttpRequest();
xhr.responseType = "arraybuffer";
xhr.onload = function () {
  callback(toBase64(xhr.response));
};
xhr.onerror = function () {
  callback(xhr.status);
};
xhr.open("GET", uri);
xhr.send();
'''

CLASSES_NAME = {
    'FULL_CHAT': '_3nbHh',
    'CHAT_ROW': 'hY_ET',
    'CHAT_MESSAGE': 'span.selectable-text',
    'TIMESTAMP': 'cm280p3y',
    'SENDER_INFO': 'copyable-text',
    'IMAGE_SELECTOR': 'img.jciay5ix',
    'DATA_ID': 'data-id',
    'COPYABLE_TEXT': 'div.copyable-text',


}
