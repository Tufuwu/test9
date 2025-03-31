// @flow
import configureTestStore from "redux-asserts"
import { assert } from "chai"

import rootReducer from "../reducers"

describe("discussions frontpage reducer", () => {
  let store

  beforeEach(() => {
    store = configureTestStore(rootReducer)
  })

  it("should have some initial state", () => {
    const state = store.getState().discussionsFrontpage
    assert.deepEqual(state, {
      loaded:     false,
      processing: false,
      data:       []
    })
  })
})
