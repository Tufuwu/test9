// @flow
import R from "ramda"

import {
  START_CHANNEL_EDIT,
  UPDATE_CHANNEL_EDIT,
  UPDATE_CHANNEL_ERRORS,
  CLEAR_CHANNEL_EDIT
} from "../actions/channels"
import { discussionErrors } from "../lib/validation/discussions"

import type { Action } from "../flow/reduxTypes"
import type { ChannelInputs, ChannelState } from "../flow/discussionTypes"

export const NEW_CHANNEL_EDIT: ChannelInputs = {
  name:         "",
  title:        "",
  description:  "",
  channel_type: "private"
}

export const INITIAL_CHANNEL_STATE: ChannelState = {
  inputs:               { ...NEW_CHANNEL_EDIT },
  validationErrors:     {},
  validationVisibility: {},
  filters:              [],
  searchkit:            {}
}

export const channelDialog = (
  state: ChannelState = INITIAL_CHANNEL_STATE,
  action: Action<any, null>
) => {
  switch (action.type) {
  case START_CHANNEL_EDIT: {
    const startInputs = {
      ...NEW_CHANNEL_EDIT,
      ...action.payload.inputs
    }
    const newState = {
      ...state,
      filters:          R.propOr([], "filters", action.payload),
      inputs:           startInputs,
      validationErrors: discussionErrors(startInputs),
      searchkit:        action.payload.searchkit || {}
    }
    return newState
  }
  case UPDATE_CHANNEL_ERRORS: {
    return {
      ...state,
      validationErrors: {
        ...action.payload
      }
    }
  }
  case UPDATE_CHANNEL_EDIT: {
    const inputs = {
      ...state.inputs,
      ...action.payload.inputs
    }
    return {
      ...state,
      inputs:               inputs,
      validationErrors:     discussionErrors(inputs),
      validationVisibility: {
        ...state.validationVisibility,
        ...action.payload.validationVisibility
      }
    }
  }
  case CLEAR_CHANNEL_EDIT:
    return R.clone(INITIAL_CHANNEL_STATE)
  default:
    return state
  }
}
