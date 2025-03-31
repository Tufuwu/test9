// @flow
import { createAction } from "redux-actions"

export const qualifiedName = (name: string) => `CHANNEL_DIALOG_${name}`

export const START_CHANNEL_EDIT = qualifiedName("START_CHANNEL_EDIT")
export const startChannelEdit = createAction(START_CHANNEL_EDIT)

export const UPDATE_CHANNEL_EDIT = qualifiedName("UPDATE_CHANNEL_EDIT")
export const updateChannelEdit = createAction(UPDATE_CHANNEL_EDIT)

export const UPDATE_CHANNEL_ERRORS = qualifiedName("UPDATE_CHANNEL_ERRORS")
export const updateChannelErrors = createAction(UPDATE_CHANNEL_ERRORS)

export const CLEAR_CHANNEL_EDIT = qualifiedName("CLEAR_CHANNEL_EDIT")
export const clearChannelEdit = createAction(CLEAR_CHANNEL_EDIT)
