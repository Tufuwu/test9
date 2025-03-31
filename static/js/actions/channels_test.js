// @flow
import {
  startChannelEdit,
  updateChannelEdit,
  clearChannelEdit,
  START_CHANNEL_EDIT,
  UPDATE_CHANNEL_EDIT,
  CLEAR_CHANNEL_EDIT
} from "./channels"
import { assertCreatedActionHelper } from "./test_util"

describe("generated channelsEndpoint action helpers", () => {
  it("should create all action creators", () => {
    [
      [startChannelEdit, START_CHANNEL_EDIT],
      [updateChannelEdit, UPDATE_CHANNEL_EDIT],
      [clearChannelEdit, CLEAR_CHANNEL_EDIT]
    ].forEach(assertCreatedActionHelper)
  })
})
