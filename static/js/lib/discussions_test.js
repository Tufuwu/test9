// @flow
/* global SETTINGS: false */
import { assert } from "chai"

import { channelURL, postURL, frontpageAPI } from "./discussions"

describe("open-discussions utility functions", () => {
  it("channelURL should behave as expected", () => {
    [
      ["channelname", "http://open.discussions/channel/channelname"],
      ["/channelname", "http://open.discussions/channel/channelname"],
      ["/channelname/", "http://open.discussions/channel/channelname/"],
      ["channelname/", "http://open.discussions/channel/channelname/"]
    ].forEach(([channelName, expectation]) => {
      assert.equal(channelURL(channelName), expectation)
    })
  })

  it("postURL should behave as expected", () => {
    [
      ["/post", "channel", "http://open.discussions/channel/channel/post"],
      ["/post/", "channel", "http://open.discussions/channel/channel/post/"],
      ["/post", "/channel", "http://open.discussions/channel/channel/post"],
      ["/post/", "channel/", "http://open.discussions/channel/channel/post/"],
      ["post", "/channel/", "http://open.discussions/channel/channel/post"]
    ].forEach(([postID, channelName, expectation]) => {
      assert.equal(postURL(postID, channelName), expectation)
    })
  })

  it("frontpageAPI should behave as expected", () => {
    [
      ["http://open.discussions", "http://open.discussions/api/v0/frontpage/"],
      ["http://open.discussions/", "http://open.discussions/api/v0/frontpage/"],
      [
        "http://open.discussions/foobar/",
        "http://open.discussions/foobar/api/v0/frontpage/"
      ]
    ].forEach(([redirectURL, expectation]) => {
      SETTINGS.open_discussions_redirect_url = redirectURL
      assert.equal(frontpageAPI(), expectation)
    })
  })
})
