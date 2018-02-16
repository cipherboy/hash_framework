module HashFramework.Codec where

import Prelude

import Data.Bifunctor (lmap)
import Data.Codec (basicCodec, composeCodec, encode)
import Data.Codec.Argonaut (JsonCodec, JsonDecodeError(..), boolean, int, object, record, recordProp, string)
import Data.DateTime (DateTime)
import Data.Formatter.DateTime as F.DT
import Data.List (fromFoldable)
import Data.Symbol (SProxy(..))
import HashFramework.Types (Task)

task :: JsonCodec Task
task = object "Task"
  $ recordProp (SProxy :: SProxy "id") int
  $ recordProp (SProxy :: SProxy "name") string
  $ recordProp (SProxy :: SProxy "algo") string
  $ recordProp (SProxy :: SProxy "priority") int
  $ recordProp (SProxy :: SProxy "running") boolean
  $ recordProp (SProxy :: SProxy "started") datetime
  $ recordProp (SProxy :: SProxy "remaining_jobs") int
  $ recordProp (SProxy :: SProxy "total_jobs") int
  $ recordProp (SProxy :: SProxy "current_threads") int
  $ recordProp (SProxy :: SProxy "max_threads") int
  $ record

fmt :: F.DT.Formatter
fmt = fromFoldable
  [ F.DT.DayOfWeekNameShort
  , F.DT.Placeholder ", "
  , F.DT.DayOfMonth
  , space
  , F.DT.MonthShort
  , space
  , F.DT.YearFull
  , space
  , F.DT.Hours24
  , colon
  , F.DT.MinutesTwoDigits
  , colon
  , F.DT.SecondsTwoDigits
  , space
  , F.DT.Placeholder "GMT"
  ]
  where
    space = F.DT.Placeholder " "
    colon = F.DT.Placeholder ":"

datetime :: JsonCodec DateTime
datetime = basicCodec
  (\e -> F.DT.unformat fmt e # mapError e)
  (F.DT.format fmt) `composeCodec` string
  where mapError e = lmap (const (UnexpectedValue (encode string e)))
