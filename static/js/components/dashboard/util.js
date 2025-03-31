// @flow
import _ from "lodash"

export const formatGrade = (grade: ?number | ?string | null): string => {
  if (_.isNil(grade) || grade === "") {
    return ""
  } else {
    grade = Number(grade)
    // isFinite will return true for numbers, false for strings and NaN
    return _.isFinite(grade) ? `${_.round(grade)}%` : ""
  }
}
