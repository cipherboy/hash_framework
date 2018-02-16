module HashFramework.Types where

import Data.DateTime (DateTime)

type TaskR r =
  { "id" :: Int
  , "name" :: String
  , "algo" :: String
  , "priority" :: Int
  , "running" :: Boolean
  , "started" :: DateTime
  , "remaining_jobs" :: Int
  , "total_jobs" :: Int
  , "current_threads" :: Int
  , "max_threads" :: Int
  | r
  }
type Task = TaskR ()
type Tasks = Array Task
