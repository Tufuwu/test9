// @flow

export type Post = {
  id:            string,
  title:         string,
  author_id:     string,  // username
  score:         number,
  upvoted:       boolean,
  url:           ?string,
  text:          ?string,
  created:       string,
  num_comments:  number,
  channel_name:  string,
  profile_image: string,
}

type ChannelType = "private" | "public";

export type ChannelInputs = {
  name:         string,
  title:        string,
  description:  string,
  channel_type: ChannelType,
};

export type Filter = {
  id:    string,
  name?: string,
  value: string
};

export type ChannelValidationErrors = {
  name?:               string,
  title?:              string,
  description?:        string,
};

export type ChannelState = {
  inputs:               ChannelInputs,
  validationErrors:     ChannelValidationErrors,
  validationVisibility: { [string]: bool },
  filters:              ?Array<Filter>,
  searchkit:            Object
};

export type CreateChannelResponse = {
  name:               string,
  title:              string,
  description:        string,
  channel_type:       ChannelType,
  query:              Object
};
